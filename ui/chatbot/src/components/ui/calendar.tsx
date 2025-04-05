import React, { useEffect, useState } from "react";
import { Calendar, momentLocalizer } from "react-big-calendar";
import moment from "moment";
import "react-big-calendar/lib/css/react-big-calendar.css";

const localizer = momentLocalizer(moment);

const MyCalendar = () => {
  const [events, setEvents] = useState([]);
  useEffect(() => {
    // Simulate fetching data
    setTimeout(() => {
      const fetchedEvents = [
        {
          title: "Meeting",
          start: new Date(2025, 3, 1, 10, 0), // April 1, 2025, 10:00 AM
          end: new Date(2025, 3, 1, 12, 0), // April 1, 2025, 12:00 PM
        },
        {
          title: "Lunch Break",
          start: new Date(2025, 3, 1, 13, 0), // April 1, 2025, 1:00 PM
          end: new Date(2025, 3, 1, 14, 0), // April 1, 2025, 2:00 PM
        },
      ];
      setEvents(fetchedEvents);
    }, 1000);
  }, []);
  return (
    <div style={{ height: 700 }}>
      <Calendar
        localizer={localizer}
        events={events}
        startAccessor="start"
        endAccessor="end"
        style={{ height: 500 }}
        views={["week"]}
        defaultView="week"
      />
    </div>
  );
};

export default MyCalendar;
