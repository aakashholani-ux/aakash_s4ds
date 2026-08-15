const hackathonsInMemory = require("../data/hackathons");
const HackathonModel = require("../models/Hackathon");
const { getIsConnected } = require("../config/db");

// Create a new hackathon
const createHackathon = async (req, res) => {
  try {
    const {
      title,
      description,
      rules,
      timeline,
      date,
      submissionDeadline,
      location,
      prizePool
    } = req.body;

    // Required fields
    if (!title || !description || !date || !submissionDeadline) {
      return res.status(400).json({
        message:
          "Title, description, date, and submission deadline are required."
      });
    }

    // Validate submission deadline
    const parsedDeadline = new Date(submissionDeadline);

    if (isNaN(parsedDeadline.getTime())) {
      return res.status(400).json({
        message: "Invalid submission deadline."
      });
    }

    if (getIsConnected()) {
      // Generate next ID
      const lastHackathon = await HackathonModel.findOne().sort({ id: -1 });
      const newId = lastHackathon ? lastHackathon.id + 1 : 1;

      const newHackathon = await HackathonModel.create({
        id: newId,
        title,
        description,
        rules: rules || "",
        timeline: timeline || "",
        date,
        submissionDeadline: parsedDeadline,
        location: location || "",
        prizePool: prizePool || ""
      });

      return res.status(201).json({
        message: "Hackathon created successfully.",
        hackathon: newHackathon
      });
    }

    // Fallback to in-memory data
    const newId =
      hackathonsInMemory.length > 0
        ? Math.max(...hackathonsInMemory.map((h) => h.id)) + 1
        : 1;

    const newHackathon = {
      id: newId,
      title,
      description,
      rules: rules || "",
      timeline: timeline || "",
      date,
      submissionDeadline: parsedDeadline.toISOString(),
      location: location || "",
      prizePool: prizePool || ""
    };

    hackathonsInMemory.push(newHackathon);

    return res.status(201).json({
      message: "Hackathon created successfully.",
      hackathon: newHackathon
    });
  } catch (error) {
    console.error("Create hackathon error:", error);

    return res.status(500).json({
      message: "Server error while creating hackathon."
    });
  }
};

// Read all hackathons
const getAllHackathons = async (req, res) => {
  try {
    if (getIsConnected()) {
      const dbHackathons = await HackathonModel.find();
      return res.status(200).json(dbHackathons);
    }

    return res.status(200).json(hackathonsInMemory);
  } catch (error) {
    return res.status(500).json({
      message: "Server error while fetching hackathons."
    });
  }
};

// Read single hackathon by ID
const getHackathonById = async (req, res) => {
  try {
    const hackathonId = parseInt(req.params.id, 10);

    if (getIsConnected()) {
      const dbHackathon = await HackathonModel.findOne({
        id: hackathonId
      });

      if (!dbHackathon) {
        return res.status(404).json({
          message: "Hackathon not found."
        });
      }

      return res.status(200).json(dbHackathon);
    }

    // Fallback to in-memory data
    const hackathon = hackathonsInMemory.find(
      (h) => h.id === hackathonId
    );

    if (!hackathon) {
      return res.status(404).json({
        message: "Hackathon not found."
      });
    }

    return res.status(200).json(hackathon);
  } catch (error) {
    return res.status(500).json({
      message: "Server error while fetching hackathon."
    });
  }
};

// Update an existing hackathon
const updateHackathon = async (req, res) => {
  try {
    const hackathonId = parseInt(req.params.id, 10);

    const {
      title,
      description,
      rules,
      timeline,
      date,
      submissionDeadline,
      location,
      prizePool
    } = req.body;

    // Validate deadline if provided
    let parsedDeadline;

    if (submissionDeadline !== undefined) {
      parsedDeadline = new Date(submissionDeadline);

      if (isNaN(parsedDeadline.getTime())) {
        return res.status(400).json({
          message: "Invalid submission deadline."
        });
      }
    }

    if (getIsConnected()) {
      const updateData = {
        title,
        description,
        rules,
        timeline,
        date,
        location,
        prizePool
      };

      if (parsedDeadline) {
        updateData.submissionDeadline = parsedDeadline;
      }

      const updatedHackathon =
        await HackathonModel.findOneAndUpdate(
          { id: hackathonId },
          {
            $set: updateData
          },
          { new: true }
        );

      if (!updatedHackathon) {
        return res.status(404).json({
          message: "Hackathon not found."
        });
      }

      return res.status(200).json(updatedHackathon);
    }

    // Fallback to in-memory data
    const hackathonIndex = hackathonsInMemory.findIndex(
      (h) => h.id === hackathonId
    );

    if (hackathonIndex === -1) {
      return res.status(404).json({
        message: "Hackathon not found."
      });
    }

    if (title !== undefined) {
      hackathonsInMemory[hackathonIndex].title = title;
    }

    if (description !== undefined) {
      hackathonsInMemory[hackathonIndex].description = description;
    }

    if (rules !== undefined) {
      hackathonsInMemory[hackathonIndex].rules = rules;
    }

    if (timeline !== undefined) {
      hackathonsInMemory[hackathonIndex].timeline = timeline;
    }

    if (date !== undefined) {
      hackathonsInMemory[hackathonIndex].date = date;
    }

    if (submissionDeadline !== undefined) {
      hackathonsInMemory[hackathonIndex].submissionDeadline =
        parsedDeadline.toISOString();
    }

    if (location !== undefined) {
      hackathonsInMemory[hackathonIndex].location = location;
    }

    if (prizePool !== undefined) {
      hackathonsInMemory[hackathonIndex].prizePool = prizePool;
    }

    return res.status(200).json(
      hackathonsInMemory[hackathonIndex]
    );
  } catch (error) {
    console.error("Update hackathon error:", error);

    return res.status(500).json({
      message: "Server error while updating hackathon."
    });
  }
};

// Delete a hackathon
const deleteHackathon = async (req, res) => {
  try {
    const hackathonId = parseInt(req.params.id, 10);

    if (getIsConnected()) {
      const deletedHackathon =
        await HackathonModel.findOneAndDelete({
          id: hackathonId
        });

      if (!deletedHackathon) {
        return res.status(404).json({
          message: "Hackathon not found."
        });
      }

      return res.status(200).json({
        message: "Hackathon deleted successfully.",
        hackathon: deletedHackathon
      });
    }

    // Fallback to in-memory data
    const hackathonIndex = hackathonsInMemory.findIndex(
      (h) => h.id === hackathonId
    );

    if (hackathonIndex === -1) {
      return res.status(404).json({
        message: "Hackathon not found."
      });
    }

    const deleted = hackathonsInMemory.splice(
      hackathonIndex,
      1
    );

    return res.status(200).json({
      message: "Hackathon deleted successfully.",
      hackathon: deleted[0]
    });
  } catch (error) {
    console.error("Delete hackathon error:", error);

    return res.status(500).json({
      message: "Server error while deleting hackathon."
    });
  }
};

module.exports = {
  createHackathon,
  getAllHackathons,
  getHackathonById,
  updateHackathon,
  deleteHackathon
};