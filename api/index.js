/**
 * FileSure Internship Assignment — Express API
 * Reads from MongoDB and exposes company data.
 */

const express = require("express");
const { MongoClient } = require("mongodb");

const app = express();
const PORT = process.env.PORT || 3000;
const MONGO_URI = process.env.MONGO_URI || "mongodb://localhost:27017";
const DB_NAME = "filesure";
const COLLECTION = "companies";

// CORS (allow the frontend running on any local port) 
app.use((req, res, next) => {
  res.setHeader("Access-Control-Allow-Origin", "*");
  next();
});

// MongoDB connection (module-level singleton) 
let db;

async function connectDB() {
  const client = new MongoClient(MONGO_URI, { serverSelectionTimeoutMS: 5000 });
  await client.connect();
  db = client.db(DB_NAME);
  console.log(`Connected to MongoDB — ${DB_NAME}`);
}

// Helper: returns the collection or throws a clear error
function col() {
  if (!db) throw new Error("Database not connected");
  return db.collection(COLLECTION);
}

// Routes 

/**
 * GET /companies
 * Query params:
 *   status  — e.g. "Active"          (case-insensitive)
 *   state   — e.g. "Maharashtra"     (case-insensitive)
 *   page    — 1-based page number    (default 1)
 *   limit   — records per page       (default 20, max 100)
 */
app.get("/companies", async (req, res) => {
  try {
    const { status, state } = req.query;
    const page = Math.max(1, parseInt(req.query.page) || 1);
    const limit = Math.min(100, Math.max(1, parseInt(req.query.limit) || 20));
    const skip = (page - 1) * limit;

    const filter = {};
    if (status) filter.status = { $regex: `^${status}$`, $options: "i" };
    if (state)  filter.state  = { $regex: `^${state}$`,  $options: "i" };

    const [companies, total] = await Promise.all([
      col().find(filter, { projection: { _id: 0, ingested_at: 0 } })
            .skip(skip)
            .limit(limit)
            .toArray(),
      col().countDocuments(filter),
    ]);

    res.json({
      page,
      limit,
      total,
      totalPages: Math.ceil(total / limit),
      data: companies,
    });
  } catch (err) {
    console.error("[GET /companies]", err.message);
    res.status(500).json({ error: err.message });
  }
});

/**
 * GET /companies/summary
 * Returns record counts grouped by normalised status.
 */
app.get("/companies/summary", async (req, res) => {
  try {
    const pipeline = [
      { $group: { _id: "$status", count: { $sum: 1 } } },
      { $sort: { count: -1 } },
      { $project: { _id: 0, status: "$_id", count: 1 } },
    ];
    const summary = await col().aggregate(pipeline).toArray();
    const total = summary.reduce((acc, s) => acc + s.count, 0);
    res.json({ total, breakdown: summary });
  } catch (err) {
    console.error("[GET /companies/summary]", err.message);
    res.status(500).json({ error: err.message });
  }
});

// 404 catch-all 
app.use((req, res) => {
  res.status(404).json({ error: `Route ${req.method} ${req.path} not found` });
});

// Start 
connectDB()
  .then(() => {
    app.listen(PORT, () => console.log(`API running on http://localhost:${PORT}`));
  })
  .catch((err) => {
    console.error("[FATAL] Could not connect to MongoDB:", err.message);
    process.exit(1);
  });
