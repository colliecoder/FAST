import React, { useState } from "react";
import axios from "axios";
import { Chart as ChartJS, RadialLinearScale, PointElement, LineElement, Filler, Tooltip, Legend } from "chart.js";
import { Radar } from "react-chartjs-2";

// Register Chart.js components
ChartJS.register(RadialLinearScale, PointElement, LineElement, Filler, Tooltip, Legend);


function App() {
  const [speech, setSpeech] = useState("");
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async () => {
      if (!speech.trim()) {
          setError("Please enter a speech.");
          return;
      }

      setLoading(true);
      setError("");
      setResults(null);

      try {
          const response = await axios.post("http://localhost:3001/analyze", { speech });
          setResults(response.data);
      } catch (err) {
          setError("Error analyzing speech. Please try again.");
      } finally {
          setLoading(false);
      }
  };

  const determineBackgroundColor = (scores) => {
      const maxScore = Math.max(...scores);
      if (maxScore > 400) {
          return "rgba(255, 99, 132, 0.5)"; // Red for critical concern
      } else if (maxScore > 300) {
          return "rgba(255, 205, 86, 0.5)"; // Yellow for cause for concern
      } else {
          return "rgba(75, 192, 192, 0.5)"; // Neutral blue for normal scores
      }
  };

  const radarData = results
      ? {
            labels: Object.keys(results).filter((key) => key !== "Relevant Sentences"),
            datasets: [
                {
                    label: "Speech Scores",
                    data: Object.keys(results)
                        .filter((key) => key !== "Relevant Sentences")
                        .map((key) => results[key]),
                    backgroundColor: determineBackgroundColor(
                        Object.keys(results)
                            .filter((key) => key !== "Relevant Sentences")
                            .map((key) => results[key])
                    ),
                    borderColor: "rgba(0, 0, 0, 0.5)", // Black for clear borders
                    borderWidth: 2,
                },
            ],
        }
      : null;

  const radarOptions = {
      scales: {
          r: {
              ticks: {
                  backdropColor: "transparent",
                  stepSize: 100, // Adjust for clarity
              },
              suggestedMin: 0,
              suggestedMax: 500, // Consistent scale
              grid: {
                  color: "rgba(0, 0, 0, 0.1)", // Light grid lines
              },
              angleLines: {
                  color: "rgba(0, 0, 0, 0.1)", // Light angle lines
              },
          },
      },
  };

  const flaggedCategories = results
      ? Object.keys(results)
            .filter((key) => key !== "Relevant Sentences" && results[key] > 300)
            .map((key) => ({
                category: key,
                score: results[key],
                severity: results[key] > 400 ? "Highly Concerning!" : "Concerning",
            }))
      : [];

  const highlightKeywords = (sentence, keywords) => {
      const regex = new RegExp(`(${keywords.join("|")})`, "gi");
      const parts = sentence.split(regex);

      return parts.map((part, index) =>
          keywords.some((kw) => kw.toLowerCase() === part.toLowerCase()) ? (
              <span key={index} style={{ backgroundColor: "yellow", fontWeight: "bold" }}>
                  {part}
              </span>
          ) : (
              part
          )
      );
  };

  return (
    <div style={{ fontFamily: "Arial, sans-serif", padding: "20px" }}>
        <h1>Speech Analyzer</h1>
        <textarea
            placeholder="Enter your speech here..."
            value={speech}
            onChange={(e) => setSpeech(e.target.value)}
            rows="10"
            style={{ width: "100%", padding: "10px", marginBottom: "10px" }}
        />

        <button onClick={handleSubmit} style={{ padding: "10px 20px", cursor: "pointer" }}>
            Analyze Speech
        </button>

        {loading && <p>Analyzing speech...</p>}
        {error && <p style={{ color: "red" }}>{error}</p>}

        {results && (
            <div style={{ display: "flex", marginTop: "20px" }}>
                {/* Radar Chart Section */}
                <div style={{ flex: 2, marginRight: "20px" }}>
                    <Radar data={radarData} options={radarOptions} />
                </div>

                {/* Text Highlights Section */}
                <div style={{ flex: 1, display: "flex", flexDirection: "column" }}>
                    {/* Relevant Text Highlights */}
                    <div
                        style={{
                            padding: "10px",
                            border: "1px solid #ccc",
                            backgroundColor: "#f9f9f9",
                            maxHeight: "500px",
                            overflowY: "auto",
                            marginBottom: "10px",
                        }}
                    >
                        <h3>Relevant Text Highlights</h3>
                        {results["Relevant Sentences"]?.map(({ sentence, category, keywords }, index) => (
                            <div
                                key={index}
                                style={{
                                    marginBottom: "10px",
                                    padding: "5px",
                                    backgroundColor: "#e8f4fa",
                                    border: "1px solid #ccc",
                                }}
                            >
                                <p>
                                    <strong>Category:</strong> {category}
                                </p>
                                <p>
                                    <strong>Sentence:</strong> {highlightKeywords(sentence, keywords)}
                                </p>
                            </div>
                        ))}
                    </div>

                    {/* Cause for Concern Section */}
                    <div
                        style={{
                            padding: "10px",
                            maxHeight: "200px",
                            overflowY: "auto",
                            marginTop: "20px",
                        }}
                    >
                        <h3>
                          <span style={{ color: "red" }}>&#x203C;&#xFE0F;</span> Concerning Speech:
                          </h3>
                        {flaggedCategories.length > 0 ? (
                            <ul>
                                {flaggedCategories.map((item, index) => (
                                    <li
                                        key={index}
                                        style={{
                                            color: item.severity === "Highly Concerning!" ? "red" : "orange",
                                            fontWeight: "bold",
                                            marginBottom: "5px",
                                        }}
                                    >
                                        {item.category}: {item.score} ({item.severity})
                                    </li>
                                ))}
                            </ul>
                        ) : (
                            <p style={{ color: "green", fontWeight: "bold" }}>
                                No significant concerns detected.
                            </p>
                        )}
                    </div>
                </div>
            </div>
        )}
    </div>
);
}

export default App;

