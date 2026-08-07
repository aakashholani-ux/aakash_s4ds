const mongoose = require("mongoose");

const hackathonSchema = new mongoose.Schema(
  {
    id: { type: Number, required: true, unique: true },
    title: { type: String, required: true },
    description: { type: String, required: true },
    rules: { type: String, default: "Standard hackathon rules apply." },
    timeline: { type: String, default: "TBD" },
    date: { type: String, required: true },
    location: { type: String, default: "Online" },
    prizePool: { type: String, default: "N/A" }
  },
  {
    timestamps: true
  }
);

module.exports = mongoose.model("Hackathon", hackathonSchema);
