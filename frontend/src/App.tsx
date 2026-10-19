import { BrowserRouter, NavLink, Route, Routes } from "react-router";
import { APP_NAME } from "./lib/config";
import Calendar from "./pages/Calendar";
import Login from "./pages/Login";
import Review from "./pages/Review";
import Upload from "./pages/Upload";

// Each page lives in its own file in src/pages so pairs don't edit the same file.
// Add new pages here and in the nav below.
const links = [
  { to: "/", label: "Calendar" },
  { to: "/upload", label: "Upload" },
  { to: "/review", label: "Review" },
  { to: "/login", label: "Login" },
];

function App() {
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
        <Route path="/review" element={<Review />} />
        <Route path="/login" element={<Login />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
