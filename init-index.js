db = db.getSiblingDB('helena_db');

db.img_documents.createIndex(
  { name: 1 },
  { unique: true }
);
