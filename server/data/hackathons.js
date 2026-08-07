// In-memory data store for hackathons
const hackathons = [
  {
    id: 1,
    title: "AI Innovators Hackathon 2026",
    description: "Build cutting-edge artificial intelligence solutions solving real-world challenges in healthcare, education, and sustainability.",
    rules: "1. Teams can have 1-4 members.\n2. All code must be written during the hackathon.\n3. Open-source libraries and APIs are permitted.",
    timeline: "Opening Ceremony: 09:00 AM | Hacking Begins: 10:00 AM | Mentorship: 02:00 PM | Submissions Close: 08:00 PM",
    date: "2026-09-15",
    location: "Online",
    prizePool: "₹1,00,000"
  },
  {
    id: 2,
    title: "Web3 & Fintech Buildathon",
    description: "Design decentralized financial applications, smart contracts, and Web3 user experiences for the future of fintech.",
    rules: "1. Submissions must include open Github repository and video demo.\n2. Projects will be judged on innovation, technical complexity, and design.",
    timeline: "Keynote & Problem Statements: 10:00 AM | Code Freeze: 06:00 PM | Demos & Judging: 07:00 PM",
    date: "2026-10-01",
    location: "Tech Park Auditorium, Bengaluru",
    prizePool: "₹75,000"
  },
  {
    id: 3,
    title: "Open Source Summer Hack",
    description: "Contribute to impactful open-source tools or build new utilities to empower the global developer ecosystem.",
    rules: "1. Individual or pair participation allowed.\n2. Projects must use OSI-compliant open source licenses.",
    timeline: "Kickoff Stream: 11:00 AM | Hacking Window: 24 Hours | Final Pitch Presentation: Next Day 12:00 PM",
    date: "2026-10-20",
    location: "Hybrid (Delhi Campus & Online)",
    prizePool: "₹50,000"
  },
  {
    id: 4,
    title: "GreenTech & Clean Energy Challenge",
    description: "Develop software and IoT solutions targeting carbon reduction, smart energy distribution, and waste management.",
    rules: "1. Solutions can involve software, hardware simulations, or data science models.\n2. Original work only.",
    timeline: "Orientation: 09:30 AM | Building Phase: 10:30 AM - 05:00 PM | Winner Announcement: 06:30 PM",
    date: "2026-11-05",
    location: "Online",
    prizePool: "₹80,000"
  },
  {
    id: 5,
    title: "Mobile App Sprint 2026",
    description: "Create delightful React Native, Flutter, or native mobile applications focusing on accessibility and seamless UX.",
    rules: "1. Teams up to 3 members.\n2. App must be buildable and testable via simulator or APK/IPA.",
    timeline: "Theme Reveal: 08:00 AM | Sprinting: 08:30 AM - 06:30 PM | Evaluation: 07:00 PM",
    date: "2026-11-25",
    location: "Innovation Hub, Mumbai",
    prizePool: "₹60,000"
  }
];

module.exports = hackathons;
