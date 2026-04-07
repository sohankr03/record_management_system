# Beginner's Guide: How to Setup and Run This Project

Welcome! This guide will walk you through setting up and running the FileSure project on your computer step-by-step. Don't worry if you don't have technical experience; just follow the instructions exactly as they are written.

---

## Phase 1: Install Required Software (One-Time Setup)

You need three free programs to run this project. Please download and install them in this order:

### 1. Install Node.js
Node.js helps run the backend application of the website.
1. Go to [https://nodejs.org/](https://nodejs.org/)
2. Click the button slightly on the left that says **LTS** (Recommended for Most Users) to download it.
3. Open the downloaded file and click "Next" through the standard installation. You don't need to change any default settings.

### 2. Install Python
Python is used to clean the data and put it into the database.
1. Go to [https://www.python.org/downloads/](https://www.python.org/downloads/)
2. Click the big yellow button **Download Python**.
3. **CRITICAL STEP:** When you open the downloaded installer, look at the very bottom of the first screen. You MUST check the small box that says **"Add python.exe to PATH"** before clicking "Install Now".
4. Let the installation finish.

### 3. Install MongoDB
MongoDB is the database where the company records will be saved.
1. Go to [MongoDB Community Server Download Page](https://www.mongodb.com/try/download/community)
2. Scroll down and click the green **Download** button.
3. Open the downloaded installer. Choose the **"Complete"** setup type when asked.
4. Keep the "Install MongoD as a Service" option checked (this means it will run automatically in the background, which is what we need).
5. Finish the installation.

*(Optional but Recommended: Restart your PC now to make sure all new programs are fully recognized.)*

---

## Phase 2: Start the Project in 1 Click!

Now that you have the required software installed, running the project is incredibly simple.

1. Ensure your `company_records.csv` file is inside the **`ingestion`** folder.
2. Go to the main project folder (`filesure-project`).
3. You will see a file named **`run_project.bat`** (it might just optionally show as `run_project` with a gear/window icon).
4. **Double-click** `run_project.bat`.

### What happens next?
- A friendly green-and-black screen will pop up.
- It will **automatically** clean and insert your data into the database.
- It will **automatically** download any background tool that it needs.
- It will **automatically** start the background bridge (API) and open it in a secondary black window (make sure you do not close this secondary window).
- Finally, it will **automatically** launch the FileSure Dashboard in your default Web Browser!

**You are done!** 🎉
