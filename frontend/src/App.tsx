import { BrowserRouter, NavLink, Route, Routes } from "react-router";
import { APP_NAME } from "./lib/config";
import Calendar from "./pages/Calendar";
import Login from "./pages/Login";
import Upload from "./pages/Upload";

// Each page lives in its own file in src/pages so pairs don't edit the same file.
// Popups (like the review step after upload) live in src/components.
// Add new pages here and in the nav below.
const links = [
  { to: "/", label: "Calendar" },
  { to: "/upload", label: "Upload" },
];

function App() {
  // Logged out: show only the login page, no nav. Logged in: show the app.
  // Placeholder until auth is built in #31, which replaces this with the Supabase session.
  const loggedIn = true;
  if (!loggedIn) return <Login />;

  return (
    <BrowserRouter>
      <nav className="flex items-center gap-4 border-b px-6 py-3">
        <span className="text-xl font-bold text-blue-600">{APP_NAME}</span>
        {links.map((link) => (
          <NavLink
            key={link.to}
            to={link.to}
            end
            className={({ isActive }) => (isActive ? "font-semibold text-blue-600" : "text-gray-600")}
          >
            {link.label}
          </NavLink>
        ))}
      </nav>
      <Routes>
        <Route path="/" element={<Calendar />} />
        <Route path="/upload" element={<Upload />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
