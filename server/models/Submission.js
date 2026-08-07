const mongoose = require("mongoose");

const submissionSchema = new mongoose.Schema(
  {
    id: { type: Number, required: true, unique: true },
    hackathonId: { type: Number, required: true },
    teamName: { type: String, required: true },
    projectName: { type: String, required: true },
    githubUrl: { type: String, required: true },
    demoUrl: { type: String, default: "" },
    description: { type: String, required: true },
    submittedAt: { type: Date, default: Date.now }
  },
  {
    timestamps: true
  }
);

module.exports = mongoose.model("Submission", submissionSchema);
