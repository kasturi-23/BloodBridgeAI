<<<<<<< HEAD
import { Routes, Route } from 'react-router-dom'
import { Navbar } from './components/Navbar'
import Home from './pages/Home'
import NewRequest from './pages/NewRequest'
import RequestDashboard from './pages/RequestDashboard'
import Donors from './pages/Donors'

export default function App() {
  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      <main>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/new-request" element={<NewRequest />} />
          <Route path="/request/:requestId" element={<RequestDashboard />} />
          <Route path="/donors" element={<Donors />} />
        </Routes>
      </main>
    </div>
  )
=======
import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";

import Navbar from "./components/Navbar";
import Sidebar from "./components/Sidebar";
import Analytics from "./pages/Analytics";
import CreateRequest from "./pages/CreateRequest";
import Dashboard from "./pages/Dashboard";
import DonorDetails from "./pages/DonorDetails";
import Donors from "./pages/Donors";
import MatchResults from "./pages/MatchResults";
import Notifications from "./pages/Notifications";

function AppLayout() {
  return (
    <div className="min-h-screen p-4 lg:p-6">
      <Navbar />
      <div className="grid gap-4 lg:grid-cols-[260px_1fr]">
        <Sidebar />
        <main className="space-y-4">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/requests/new" element={<CreateRequest />} />
            <Route path="/donors" element={<Donors />} />
            <Route path="/donors/:donorId" element={<DonorDetails />} />
            <Route path="/matches/:requestId" element={<MatchResults />} />
            <Route path="/notifications" element={<Notifications />} />
            <Route path="/analytics" element={<Analytics />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </main>
      </div>
    </div>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <AppLayout />
    </BrowserRouter>
  );
>>>>>>> a3f81144c587ef50313ffd6654e433970229adef
}
