import React, { useEffect, useState } from "react";
import {
  Calendar,
  momentLocalizer,
  SlotInfo,
  Event as CalendarEvent,
} from "react-big-calendar";
import moment from "moment";
import "react-big-calendar/lib/css/react-big-calendar.css";

const localizer = momentLocalizer(moment);

interface Event {
  title: string;
  start: Date;
  end: Date;
}

const MyCalendar = () => {
  const [events, setEvents] = useState<Event[]>([]);
  const [modalOpen, setModalOpen] = useState(false);
  const [isEditing, setIsEditing] = useState(false);
  const [editingIndex, setEditingIndex] = useState<number | null>(null);
  const [newEvent, setNewEvent] = useState<Event>({
    title: "",
    start: new Date(),
    end: new Date(),
  });

  const [score, setScore] = useState<number | null>(null);
  const [recommendation, setRecommendation] = useState<{ hour: number; activity: string }[]>([]);

  useEffect(() => {
    setTimeout(() => {
      const fetchedEvents = [
        {
          title: "Meeting",
          start: new Date(2025, 3, 1, 10, 0),
          end: new Date(2025, 3, 1, 12, 0),
        },
        {
          title: "Lunch Break",
          start: new Date(2025, 3, 1, 13, 0),
          end: new Date(2025, 3, 1, 14, 0),
        },
      ];
      setEvents(fetchedEvents);
    }, 1000);
  }, []);

  const handleSelectSlot = (slotInfo: SlotInfo) => {
    setNewEvent({
      title: "",
      start: slotInfo.start,
      end: slotInfo.end,
    });
    setIsEditing(false);
    setModalOpen(true);
  };

  const handleSelectEvent = (event: CalendarEvent) => {
    const index = events.findIndex(
      (e) =>
        e.start.getTime() === event.start.getTime() &&
        e.end.getTime() === event.end.getTime() &&
        e.title === event.title
    );
    if (index !== -1) {
      setNewEvent(events[index]);
      setEditingIndex(index);
      setIsEditing(true);
      setModalOpen(true);
    }
  };

  const hasConflict = (event: Event, excludeIndex: number | null = null) => {
    return events.some((e, idx) => {
      if (excludeIndex !== null && idx === excludeIndex) return false;

      const existingStart = new Date(e.start).getTime();
      const existingEnd = new Date(e.end).getTime();
      const newStart = new Date(event.start).getTime();
      const newEnd = new Date(event.end).getTime();

      return (
        (newStart >= existingStart && newStart < existingEnd) ||
        (newEnd > existingStart && newEnd <= existingEnd) ||
        (newStart <= existingStart && newEnd >= existingEnd)
      );
    });
  };

  const handleSave = () => {
    if (hasConflict(newEvent, isEditing ? editingIndex : null)) {
      alert("This time slot is already occupied by another event.");
      return;
    }

    if (isEditing && editingIndex !== null) {
      const updated = [...events];
      updated[editingIndex] = newEvent;
      setEvents(updated);
    } else {
      setEvents([...events, newEvent]);
    }

    closeModal();
  };

  const handleDelete = () => {
    if (isEditing && editingIndex !== null) {
      const updated = [...events];
      updated.splice(editingIndex, 1);
      setEvents(updated);
    }
    closeModal();
  };

  const closeModal = () => {
    setModalOpen(false);
    setIsEditing(false);
    setEditingIndex(null);
    setNewEvent({ title: "", start: new Date(), end: new Date() });
  };

  // convert agenda to actvity and split to each hour
  const convertEventsToHourlySchedule = (events: Event[]) => {
    const result: { hour: number; activity: string }[] = [];

    events.forEach((event) => {
      const startHour = event.start.getHours();
      const endHour = event.end.getHours();

      for (let h = startHour; h < endHour; h++) {
        result.push({ hour: h, activity: event.title });
      }
    });

    return result;
  };

  
  // press grading - websocket
  const handleScore = () => {
    const scheduleData = convertEventsToHourlySchedule(events);
    const socket = new WebSocket("ws://localhost:8090");

    socket.onopen = () => {
      socket.send(
        JSON.stringify({
          type: "score",
          events: scheduleData,
        })
      );
    };

    socket.onmessage = (event) => {
      if (event.data === "[END]") return;

      const data = JSON.parse(event.data);
      if (data.type === "score_result") {
        setScore(data.score);
        alert(`🧠 Health Score：${data.score}`);
      }
    };
  };

  const handleRecommend = () => {
    const socket = new WebSocket("ws://localhost:8090");
  
    socket.onopen = () => {
      socket.send(JSON.stringify({ type: "recommend" }));
    };
  
    socket.onmessage = (event) => {
      if (event.data === "[END]") return;
  
      const data = JSON.parse(event.data);
      if (data.type === "recommend_result") {
        setRecommendation(data.schedule);
      }
    };
  };
  

  return (
    <div style={{ height: 700 }} className="relative">
      <Calendar
        localizer={localizer}
        events={events}
        startAccessor="start"
        endAccessor="end"
        style={{ height: 500 }}
        views={["week"]}
        defaultView="week"
        selectable
        onSelectSlot={handleSelectSlot}
        onSelectEvent={handleSelectEvent}
      />

      {score !== null && (
        <div className="text-center text-lg mt-4">
          🧠 Current Health Score：<strong>{score}</strong>
        </div>
      )}

      <div className="flex justify-center gap-4 mt-4">
        <button
          className="bg-green-600 text-white px-4 py-2 rounded"
          onClick={handleScore}
        >
          Grading
        </button>
        <button
          className="bg-blue-600 text-white px-4 py-2 rounded"
          onClick={handleRecommend}
        >
          See Recommendation
        </button>
      </div>

      {recommendation.length > 0 && (
        <div className="text-left mt-6 px-4 max-w-lg mx-auto">
          <h3 className="text-lg font-semibold mb-2"> Recommended Schdule：</h3>
          <ul className="list-disc pl-4">
            {recommendation.map((item) => (
              <li key={item.hour}>
                {item.hour.toString().padStart(2, "0")}:00 → {item.activity}
              </li>
            ))}
          </ul>
        </div>
      )}


      {modalOpen && (
        <div className="absolute top-10 left-1/2 transform -translate-x-1/2 bg-white shadow-lg rounded-lg p-6 z-50 w-96 border border-gray-300">
          <h2 className="text-lg font-bold mb-4">
            {isEditing ? "Edit Event" : "Add New Event"}
          </h2>
          <label className="block mb-2 text-sm">Title</label>
          <input
            className="w-full border px-2 py-1 mb-4 rounded"
            value={newEvent.title}
            onChange={(e) =>
              setNewEvent({ ...newEvent, title: e.target.value })
            }
          />
          <label className="block text-sm mb-1">
            Start: {newEvent.start.toLocaleString()}
          </label>
          <label className="block text-sm mb-4">
            End: {newEvent.end.toLocaleString()}
          </label>

          <div className="flex justify-between items-center mt-4">
            {isEditing && (
              <button
                className="text-red-600 font-medium"
                onClick={handleDelete}
              >
                Delete
              </button>
            )}
            <div className="flex gap-2 ml-auto">
              <button
                className="bg-gray-300 px-4 py-2 rounded"
                onClick={closeModal}
              >
                Cancel
              </button>
              <button
                className="bg-blue-600 text-white px-4 py-2 rounded"
                onClick={handleSave}
                disabled={!newEvent.title}
              >
                {isEditing ? "Update" : "Save"}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default MyCalendar;
