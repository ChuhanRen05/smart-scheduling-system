import { Textarea } from "../ui/textarea";
import { cx } from "classix";
import { Button } from "../ui/button";
import { ArrowUpIcon } from "./icons";
import { toast } from "sonner";
import { motion } from "framer-motion";
import { useState } from "react";

interface ChatInputProps {
  question: string;
  setQuestion: (question: string) => void;
  onSubmit: (text?: string) => void;
  isLoading: boolean;
  onShowCalendar: () => void;
  isCalendarVisible: boolean;
}

export const ChatInput = ({
  question,
  setQuestion,
  onSubmit,
  isLoading,
  onShowCalendar,
  isCalendarVisible,
}: ChatInputProps) => {
  return (
    <div className="relative w-full flex flex-col gap-4">
      <input
        type="file"
        className="fixed -top-4 -left-4 size-0.5 opacity-0 pointer-events-none"
        multiple
        tabIndex={-1}
      />
      <Button
        onClick={onShowCalendar}
        className="text-left border rounded-xl px-4 py-3.5 text-sm flex-1 gap-1 sm:flex-col w-full h-auto justify-start items-start"
      >
        {isCalendarVisible ? "Hide the calendar" : "Show the calendar"}
      </Button>

      <Textarea
        placeholder="Send a message..."
        className={cx(
          "min-h-[24px] max-h-[calc(75dvh)] overflow-hidden resize-none rounded-xl text-base bg-muted"
        )}
        value={question}
        onChange={(e) => setQuestion(e.target.value)}
        onKeyDown={(event) => {
          if (event.key === "Enter" && !event.shiftKey) {
            event.preventDefault();

            if (isLoading) {
              toast.error("Please wait for the model to finish its response!");
            } else {
              onSubmit();
            }
          }
        }}
        rows={3}
        autoFocus
      />

      <Button
        className="rounded-full p-1.5 h-fit absolute bottom-2 right-2 m-0.5 border dark:border-zinc-600"
        onClick={() => onSubmit(question)}
        disabled={question.length === 0}
      >
        <ArrowUpIcon size={14} />
      </Button>
    </div>
  );
};
