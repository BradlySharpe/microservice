from flask import jsonify
from controllers.ziprecruiter import ZipRecruiter
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Ensure the logger is thread safe
thread_safe_handler = logging.StreamHandler()
formatter = logging.Formatter('%(levelname)s - %(message)s')
thread_safe_handler.setFormatter(formatter)
logger.addHandler(thread_safe_handler)

def get_fetch():
    try:
        zip_recruiter = ZipRecruiter(logger)
        return jsonify({
            "error": None,
            "mapper": "ziprecruiter",
            "data": zip_recruiter.get_jobs()
        }), 200
    except Exception as e:
        logger.error(f"Failed to fetch jobs: {e}")
        return jsonify({
            "error": "An unknown error occurred",
            "mapper": "ziprecruiter",
            "data": None
        }), 500
    