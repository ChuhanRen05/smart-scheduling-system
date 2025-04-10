import { motion } from "framer-motion";
import { MessageCircle } from "lucide-react";
import { Button } from "../ui/button";
import MyCalendar from "../ui/calendar";
import HealthScore from "./health-score";

export const Overview = () => {
  const mockScore = 88; // Replace with real score

  return (
    <div className="relative">
      <HealthScore score={mockScore} />

      <motion.div
        key="overview"
        className="max-w-3xl mx-auto md:mt-20"
        initial={{ opacity: 0, scale: 0.98 }}
        animate={{ opacity: 1, scale: 1 }}
        exit={{ opacity: 0, scale: 0.98 }}
        transition={{ delay: 0.75 }}
      >
        <div className="rounded-xl p-6 flex flex-col gap-8 leading-relaxed text-center max-w-xl">
          <p className="flex flex-row justify-center gap-4 items-center"></p>
          <p>Welcome to the Smart Calendar.</p>
          <p>
            I'm your schedule assistant. What's your name? (Add @ before your
            name)
          </p>
          {/* <p>Ready to create some events?</p> */}
          {/* <MyCalendar /> */}
        </div>
      </motion.div>
    </div>
  );
};
