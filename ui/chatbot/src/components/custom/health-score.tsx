import React from "react";

interface HealthScoreProps {
  score: number;
}

const HealthScore: React.FC<HealthScoreProps> = ({ score }) => {
  let bgColor = "bg-green-600";
  if (score <= 79 && score >= 50) {
    bgColor = "bg-yellow-500";
  } else if (score < 50) {
    bgColor = "bg-red-600";
  }

  return (
    <div
      className={`absolute top-4 right-4 ${bgColor} text-white px-6 py-3 rounded-full shadow-lg font-bold text-2xl z-50`}
    >
      Health Score: {score}
    </div>
  );
};

export default HealthScore;
