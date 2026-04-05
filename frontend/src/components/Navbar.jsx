<<<<<<< HEAD
import { Link, useLocation } from 'react-router-dom'
import { Droplets, LayoutDashboard, Users, PlusCircle } from 'lucide-react'

export function Navbar() {
  const { pathname } = useLocation()

  const links = [
    { to: '/', label: 'Dashboard', icon: LayoutDashboard },
    { to: '/new-request', label: 'New Request', icon: PlusCircle },
    { to: '/donors', label: 'Donors', icon: Users },
  ]

  return (
    <nav className="bg-white border-b border-gray-200 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link to="/" className="flex items-center gap-2.5">
            <div className="bg-red-600 text-white p-1.5 rounded-lg">
              <Droplets size={20} />
            </div>
            <span className="font-bold text-xl text-gray-900">BloodBridge</span>
            <span className="text-xs bg-red-50 text-red-600 px-2 py-0.5 rounded-full font-medium">
              Emergency
            </span>
          </Link>

          {/* Nav links */}
          <div className="flex items-center gap-1">
            {links.map(({ to, label, icon: Icon }) => (
              <Link
                key={to}
                to={to}
                className={`flex items-center gap-1.5 px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                  pathname === to
                    ? 'bg-red-50 text-red-700'
                    : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
                }`}
              >
                <Icon size={15} />
                {label}
              </Link>
            ))}
          </div>
        </div>
      </div>
    </nav>
  )
=======
export default function Navbar() {
  return (
    <header className="card mb-4 flex items-center justify-between px-5 py-3">
      <div>
        <h1 className="text-xl font-bold text-primary">Emergency Blood Donor Coordination</h1>
        <p className="text-xs text-slate-500">Hackathon Prototype Workflow</p>
      </div>
      <div className="rounded-lg bg-red-50 px-3 py-2 text-xs font-semibold text-critical">Live Alerts Enabled</div>
    </header>
  );
>>>>>>> a3f81144c587ef50313ffd6654e433970229adef
}
