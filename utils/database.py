import os
import sqlite3

import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv


# ========================================
# LOAD ENVIRONMENT
# ========================================

load_dotenv()


# ========================================
# DATABASE MODE
# ========================================

DATABASE_URL = os.getenv("DATABASE_URL")

LOCAL_DB_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "interview_preparation.db"
)


def using_postgresql():
    """
    Return True when DATABASE_URL is available.
    Otherwise use local SQLite database.
    """

    return bool(DATABASE_URL)


# ========================================
# DATABASE CONNECTION
# ========================================

def get_connection():
    """
    Create a database connection.

    Local:
        SQLite

    Render:
        PostgreSQL
    """

    if using_postgresql():

        return psycopg2.connect(
            DATABASE_URL,
            cursor_factory=RealDictCursor
        )

    # Local SQLite
    connection = sqlite3.connect(
        LOCAL_DB_PATH
    )

    connection.row_factory = sqlite3.Row

    initialize_sqlite_database(
        connection
    )

    return connection


# ========================================
# SQLITE DATABASE INITIALIZATION
# ========================================

def initialize_sqlite_database(connection):
    """
    Create SQLite tables for local development.
    """

    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(100) NOT NULL,
            email VARCHAR(255) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL,
            is_admin BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS interviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            interview_type VARCHAR(100) NOT NULL,
            difficulty VARCHAR(50),
            question TEXT,
            answer TEXT,
            evaluation TEXT,
            score INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (user_id)
                REFERENCES users(id)
                ON DELETE CASCADE
        )
    """)

    connection.commit()

    cursor.close()


# ========================================
# CREATE TABLES
# ========================================

def init_db():
    """
    Initialize database tables.

    Works with both SQLite and PostgreSQL.
    """

    connection = get_connection()

    try:

        cursor = connection.cursor()

        if using_postgresql():

            # PostgreSQL Users table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    email VARCHAR(255) UNIQUE NOT NULL,
                    password VARCHAR(255) NOT NULL,
                    is_admin BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)

            # PostgreSQL Interviews table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS interviews (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER REFERENCES users(id)
                        ON DELETE CASCADE,
                    interview_type VARCHAR(100) NOT NULL,
                    difficulty VARCHAR(50),
                    question TEXT,
                    answer TEXT,
                    evaluation TEXT,
                    score INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)

        else:

            # SQLite tables are already created
            # automatically by get_connection().
            pass

        connection.commit()

        print(
            "Database tables initialized successfully."
        )

    finally:

        cursor.close()
        connection.close()


# ========================================
# CREATE USER
# ========================================

def create_user(name, email, password):
    """
    Create a new user.
    """

    connection = get_connection()

    try:

        cursor = connection.cursor()

        if using_postgresql():

            cursor.execute("""
                INSERT INTO users
                    (name, email, password)
                VALUES
                    (%s, %s, %s)
                RETURNING id, name, email, is_admin;
            """, (
                name,
                email,
                password
            ))

        else:

            cursor.execute("""
                INSERT INTO users
                    (name, email, password)
                VALUES
                    (?, ?, ?)
            """, (
                name,
                email,
                password
            ))

            user_id = cursor.lastrowid

            cursor.execute("""
                SELECT
                    id,
                    name,
                    email,
                    password,
                    is_admin
                FROM users
                WHERE id = ?
            """, (user_id,))

        user = cursor.fetchone()

        connection.commit()

        return user

    except Exception:

        connection.rollback()

        return None

    finally:

        cursor.close()
        connection.close()


# ========================================
# FIND USER BY EMAIL
# ========================================

def get_user_by_email(email):
    """
    Find a user using their email address.
    """

    connection = get_connection()

    try:

        cursor = connection.cursor()

        if using_postgresql():

            cursor.execute("""
                SELECT
                    id,
                    name,
                    email,
                    password,
                    is_admin
                FROM users
                WHERE email = %s;
            """, (email,))

        else:

            cursor.execute("""
                SELECT
                    id,
                    name,
                    email,
                    password,
                    is_admin
                FROM users
                WHERE email = ?;
            """, (email,))

        return cursor.fetchone()

    finally:

        cursor.close()
        connection.close()


# ========================================
# FIND USER BY ID
# ========================================

def get_user_by_id(user_id):
    """
    Find a user using their ID.
    """

    connection = get_connection()

    try:

        cursor = connection.cursor()

        if using_postgresql():

            cursor.execute("""
                SELECT
                    id,
                    name,
                    email,
                    is_admin
                FROM users
                WHERE id = %s;
            """, (user_id,))

        else:

            cursor.execute("""
                SELECT
                    id,
                    name,
                    email,
                    is_admin
                FROM users
                WHERE id = ?;
            """, (user_id,))

        return cursor.fetchone()

    finally:

        cursor.close()
        connection.close()


# ========================================
# SAVE INTERVIEW
# ========================================

def save_interview(
    user_id,
    interview_type,
    difficulty,
    question,
    answer,
    evaluation,
    score=None
):
    """
    Save an interview attempt.
    """

    connection = get_connection()

    try:

        cursor = connection.cursor()

        if using_postgresql():

            cursor.execute("""
                INSERT INTO interviews
                    (
                        user_id,
                        interview_type,
                        difficulty,
                        question,
                        answer,
                        evaluation,
                        score
                    )
                VALUES
                    (%s, %s, %s, %s, %s, %s, %s)
                RETURNING id;
            """, (
                user_id,
                interview_type,
                difficulty,
                question,
                answer,
                evaluation,
                score
            ))

        else:

            cursor.execute("""
                INSERT INTO interviews
                    (
                        user_id,
                        interview_type,
                        difficulty,
                        question,
                        answer,
                        evaluation,
                        score
                    )
                VALUES
                    (?, ?, ?, ?, ?, ?, ?)
            """, (
                user_id,
                interview_type,
                difficulty,
                question,
                answer,
                evaluation,
                score
            ))

        interview = cursor.fetchone()

        connection.commit()

        return interview

    finally:

        cursor.close()
        connection.close()


# ========================================
# GET USER INTERVIEW HISTORY
# ========================================

def get_user_interviews(user_id):
    """
    Get all interviews of a specific user.
    """

    connection = get_connection()

    try:

        cursor = connection.cursor()

        if using_postgresql():

            cursor.execute("""
                SELECT
                    id,
                    interview_type,
                    difficulty,
                    question,
                    answer,
                    evaluation,
                    score,
                    created_at
                FROM interviews
                WHERE user_id = %s
                ORDER BY created_at DESC;
            """, (user_id,))

        else:

            cursor.execute("""
                SELECT
                    id,
                    interview_type,
                    difficulty,
                    question,
                    answer,
                    evaluation,
                    score,
                    created_at
                FROM interviews
                WHERE user_id = ?
                ORDER BY created_at DESC;
            """, (user_id,))

        return cursor.fetchall()

    finally:

        cursor.close()
        connection.close()


# ========================================
# GET ALL USERS
# ========================================

def get_all_users():
    """
    Get all registered users.
    """

    connection = get_connection()

    try:

        cursor = connection.cursor()

        cursor.execute("""
            SELECT
                id,
                name,
                email,
                is_admin,
                created_at
            FROM users
            ORDER BY created_at DESC;
        """)

        return cursor.fetchall()

    finally:

        cursor.close()
        connection.close()


# ========================================
# GET TOTAL USERS
# ========================================

def get_total_users():
    """
    Return total number of registered users.
    """

    connection = get_connection()

    try:

        cursor = connection.cursor()

        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM users;
        """)

        result = cursor.fetchone()

        return result["total"]

    finally:

        cursor.close()
        connection.close()


# ========================================
# GET TOTAL INTERVIEWS
# ========================================

def get_total_interviews():
    """
    Return total number of interviews.
    """

    connection = get_connection()

    try:

        cursor = connection.cursor()

        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM interviews;
        """)

        result = cursor.fetchone()

        return result["total"]

    finally:

        cursor.close()
        connection.close()


# ========================================
# GET USER PERFORMANCE
# ========================================

def get_user_performance(user_id):
    """
    Get performance statistics for a specific user.
    """

    connection = get_connection()

    try:

        cursor = connection.cursor()

        if using_postgresql():

            cursor.execute("""
                SELECT
                    COUNT(*) AS total_interviews,
                    COALESCE(AVG(score), 0) AS average_score,
                    COALESCE(MAX(score), 0) AS highest_score
                FROM interviews
                WHERE user_id = %s;
            """, (user_id,))

        else:

            cursor.execute("""
                SELECT
                    COUNT(*) AS total_interviews,
                    COALESCE(AVG(score), 0) AS average_score,
                    COALESCE(MAX(score), 0) AS highest_score
                FROM interviews
                WHERE user_id = ?;
            """, (user_id,))

        overall = cursor.fetchone()


        if using_postgresql():

            cursor.execute("""
                SELECT
                    interview_type,
                    COUNT(*) AS total,
                    COALESCE(AVG(score), 0) AS average_score
                FROM interviews
                WHERE user_id = %s
                GROUP BY interview_type
                ORDER BY interview_type;
            """, (user_id,))

        else:

            cursor.execute("""
                SELECT
                    interview_type,
                    COUNT(*) AS total,
                    COALESCE(AVG(score), 0) AS average_score
                FROM interviews
                WHERE user_id = ?
                GROUP BY interview_type
                ORDER BY interview_type;
            """, (user_id,))

        by_type = cursor.fetchall()


        return {
            "total_interviews": overall["total_interviews"],
            "average_score": round(
                float(overall["average_score"]),
                2
            ),
            "highest_score": overall["highest_score"],
            "by_type": by_type
        }

    finally:

        cursor.close()
        connection.close()
        # ========================================
# GET ADMIN STATISTICS
# ========================================

def get_admin_stats():
    """
    Get overall statistics for Admin Dashboard.
    """

    connection = get_connection()

    try:

        cursor = connection.cursor()

        # ----------------------------------------
        # Total Users
        # ----------------------------------------

        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM users;
        """)

        total_users = cursor.fetchone()["total"]

        # ----------------------------------------
        # Total Interviews
        # ----------------------------------------

        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM interviews;
        """)

        total_interviews = cursor.fetchone()["total"]

        # ----------------------------------------
        # Average Score
        # ----------------------------------------

        cursor.execute("""
            SELECT COALESCE(AVG(score), 0) AS average_score
            FROM interviews
            WHERE score IS NOT NULL;
        """)

        average_score = cursor.fetchone()["average_score"]

        # ----------------------------------------
        # Best Score
        # ----------------------------------------

        cursor.execute("""
            SELECT COALESCE(MAX(score), 0) AS best_score
            FROM interviews
            WHERE score IS NOT NULL;
        """)

        best_score = cursor.fetchone()["best_score"]

        return {
            "total_users": total_users,
            "total_interviews": total_interviews,
            "average_score": round(float(average_score), 2),
            "best_score": best_score
        }

    finally:

        cursor.close()
        connection.close()


# ========================================
# GET RECENT INTERVIEWS
# ========================================

def get_recent_interviews(limit=20):
    """
    Get recent interview attempts for Admin Dashboard.
    """

    connection = get_connection()

    try:

        cursor = connection.cursor()

        if using_postgresql():

            cursor.execute("""
                SELECT
                    interviews.id,
                    interviews.interview_type,
                    interviews.difficulty,
                    interviews.score,
                    interviews.created_at,
                    users.name,
                    users.email
                FROM interviews
                LEFT JOIN users
                    ON interviews.user_id = users.id
                ORDER BY interviews.created_at DESC
                LIMIT %s;
            """, (limit,))

        else:

            cursor.execute("""
                SELECT
                    interviews.id,
                    interviews.interview_type,
                    interviews.difficulty,
                    interviews.score,
                    interviews.created_at,
                    users.name,
                    users.email
                FROM interviews
                LEFT JOIN users
                    ON interviews.user_id = users.id
                ORDER BY interviews.created_at DESC
                LIMIT ?;
            """, (limit,))

        return cursor.fetchall()

    finally:

        cursor.close()
        connection.close()