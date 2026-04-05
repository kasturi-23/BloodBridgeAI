import { NavLink } from "react-router-dom";

const items = [
  ["/", "Dashboard"],
  ["/requests/new", "Create Request"],
  ["/donors", "Donors"],
  ["/notifications", "Notifications"],
  ["/analytics", "Analytics"],
];

export default function Sidebar() {
  return (
    <aside className="w-full lg:w-64 card p-4">
      <h2 className="mb-4 text-lg font-semibold text-primary">Blood Donor System</h2>
      <nav className="space-y-2">
        {items.map(([to, label]) => (
          <NavLink
            key={to}
            to={to}
            className={({ isActive }) =>
              `block rounded-lg px-3 py-2 text-sm font-medium ${
                isActive ? "bg-primary text-white" : "text-slate-700 hover:bg-slate-100"
              }`
            }
          >
            {label}
          </NavLink>
        ))}
      </nav>
    </aside>
  );
}
