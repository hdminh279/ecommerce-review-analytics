import os
import logging
import numpy as np
import pandas as pd
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import FloatType
from pyspark.ml import PipelineModel
from sklearn.metrics import f1_score, confusion_matrix, classification_report, accuracy_score

URL_S3_SILVER = os.environ.get("URL_S3_SILVER", "s3a://amazon-reviews-datalake/silver")
MODEL_SAVE_PATH = os.environ.get("MODEL_SAVE", "s3a://amazon-reviews-datalake/silver/model")
BINARY_MODEL_PATH = f"{MODEL_SAVE_PATH}/sentiment_binary_lsvm/class_weighting"

CATEGORIES = ["All_Beauty", "Amazon_Fashion"]
CHOSEN_THETA = 0.40  # Confidence <= 59.87% mapped to Uncertain (1.0)

def evaluate_predictions(y_true, y_pred, split_name: str, logger: logging.Logger):
    """Evaluate and log 3-class classification metrics on unseen test set."""
    acc = accuracy_score(y_true, y_pred)
    macro_f1 = f1_score(y_true, y_pred, average="macro")
    weighted_f1 = f1_score(y_true, y_pred, average="weighted")
    report = classification_report(
        y_true,
        y_pred,
        target_names=["Negative (0)", "Uncertain (1)", "Positive (2)"],
        digits=4
    )
    cm = confusion_matrix(y_true, y_pred)

    logger.info("==================================================")
    logger.info(f"[{split_name}] Accuracy    : {acc:.4f}")
    logger.info(f"[{split_name}] Weighted F1 : {weighted_f1:.4f}")
    logger.info(f"[{split_name}] Macro-F1    : {macro_f1:.4f}")
    logger.info(f"[{split_name}] Classification Report:\n{report}")
    logger.info(f"[{split_name}] Confusion Matrix:\n{cm}")
    logger.info("==================================================")
    return acc, macro_f1, weighted_f1

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
    logger = logging.getLogger("Task4_Evaluate_Test_Set")

    try:
        spark = (
            SparkSession.builder.appName("Sentiment_Task4_Holdout_Test_Evaluation")
            .master(os.environ.get("SPARK_MASTER_URL", "spark://spark-master:7077"))
            .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")
            .config("spark.hadoop.fs.s3a.access.key", os.environ.get("ACCESS_KEY"))
            .config("spark.hadoop.fs.s3a.secret.key", os.environ.get("SECRET_KEY"))
            .config("spark.hadoop.fs.s3a.endpoint", os.environ.get("MINIO_ENDPOINT", "http://minio:9000"))
            .config("spark.hadoop.fs.s3a.path.style.access", "true")
            .config("spark.executor.memory", "3g")
            .config("spark.driver.memory", "2g")
            .config("spark.driver.maxResultSize", "2g")
            .config("spark.memory.fraction", "0.8")
            .getOrCreate()
        )
        logger.info("Spark Session created successfully.")

        # 1. Load trained Binary Linear SVM PipelineModel
        logger.info(f"Loading trained Binary Linear SVM PipelineModel from: {BINARY_MODEL_PATH}")
        binary_model = PipelineModel.load(BINARY_MODEL_PATH)
        logger.info("Binary Linear SVM model loaded successfully.")

        # 2. Read unseen Hold-Out Test set
        test_path = f"{URL_S3_SILVER}/sentiment_splits/*/test"
        logger.info(f"Reading unseen Hold-Out Test data from: {test_path}")
        test_df = spark.read.parquet(test_path)
        test_count = test_df.count()
        logger.info(f"Total unseen Test rows: {test_count:,}")

        # 3. Transform test data with Binary model
        logger.info("Executing model inference on Test set...")
        predictions = binary_model.transform(test_df)

        # 4. Extract signed margin distance
        extract_margin_udf = F.udf(lambda v: float(v[1]), FloatType())
        pred_df = predictions.withColumn("margin", extract_margin_udf(F.col("rawPrediction")))

        logger.info("Collecting test ground truth labels, categories, and margins...")
        test_pd = pred_df.select("label", "margin", "category").toPandas()

        y_true = test_pd["label"].values.astype(float)
        margins = test_pd["margin"].values.astype(float)

        # 5. Comparative Evaluation Across Margin Thresholds: [0.40, 0.30, 0.20, 0.10]
        thetas_to_test = [0.40, 0.30, 0.20, 0.10]
        summary_rows = []

        for th in thetas_to_test:
            p_upper = 1.0 / (1.0 + np.exp(-th))
            conf_cap = p_upper * 100.0

            curr_y_pred = np.where(margins > th, 2.0, np.where(margins < -th, 0.0, 1.0))

            acc = accuracy_score(y_true, curr_y_pred)
            macro = f1_score(y_true, curr_y_pred, average="macro")
            weighted = f1_score(y_true, curr_y_pred, average="weighted")
            
            # Per-class recalls
            cm = confusion_matrix(y_true, curr_y_pred)
            r_neg = cm[0, 0] / cm[0].sum() if cm[0].sum() > 0 else 0.0
            r_unc = cm[1, 1] / cm[1].sum() if cm[1].sum() > 0 else 0.0
            r_pos = cm[2, 2] / cm[2].sum() if cm[2].sum() > 0 else 0.0

            summary_rows.append({
                "theta": th,
                "conf_cap": f"<= {conf_cap:.2f}%",
                "acc": f"{acc * 100:.2f}%",
                "weighted_f1": f"{weighted * 100:.2f}%",
                "macro_f1": f"{macro * 100:.2f}%",
                "r_neg": f"{r_neg * 100:.2f}%",
                "r_unc": f"{r_unc * 100:.2f}%",
                "r_pos": f"{r_pos * 100:.2f}%"
            })

            logger.info("**************************************************")
            logger.info(f"TEST EVALUATION AT THRESHOLD: theta = {th:.2f} (Confidence {summary_rows[-1]['conf_cap']})")
            logger.info("**************************************************")
            evaluate_predictions(y_true, curr_y_pred, f"OVERALL_COMBINED_TEST (theta={th:.2f})", logger)

            # Per-category evaluation
            for cat in CATEGORIES:
                cat_mask = (test_pd["category"] == cat).values
                cat_y_true = y_true[cat_mask]
                cat_y_pred = curr_y_pred[cat_mask]
                evaluate_predictions(cat_y_true, cat_y_pred, f"CATEGORY_{cat}_TEST (theta={th:.2f})", logger)

        # 6. Print Threshold Comparison Table
        logger.info("=========================================================================================")
        logger.info("SUMMARY COMPARISON TABLE ACROSS THRESHOLDS (TEST SET: 431,213 rows):")
        logger.info(f"{'Theta':<8} | {'Confidence Bound':<18} | {'Accuracy':<10} | {'Macro-F1':<10} | {'Rec Neg':<10} | {'Rec Unc':<10} | {'Rec Pos':<10}")
        logger.info("-----------------------------------------------------------------------------------------")
        for row in summary_rows:
            logger.info(f"{row['theta']:<8.2f} | {row['conf_cap']:<18} | {row['acc']:<10} | {row['macro_f1']:<10} | {row['r_neg']:<10} | {row['r_unc']:<10} | {row['r_pos']:<10}")
        logger.info("=========================================================================================")

        logger.info("Task 4 Hold-Out Test evaluation across all thresholds completed successfully.")

    except Exception as e:
        logger.error(f"Error occurred during Task 4 Test evaluation: {str(e)}", exc_info=True)
        raise
    finally:
        if "spark" in locals():
            spark.stop()
            logger.info("Spark Session stopped.")

# Execution Command:
# docker exec -it spark-master spark-submit --driver-memory 2g --executor-memory 3g /spark/nlp/TF-IDF_Linear_SVM/Margin/evaluate_test_set.py
