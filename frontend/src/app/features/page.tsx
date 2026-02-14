export default function FeaturesPage() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-50 to-slate-100">
      <div className="container mx-auto px-4 py-16">
        <h1 className="text-4xl font-bold text-center mb-4">CareOps Features</h1>
        <p className="text-center text-slate-600 mb-12">Comprehensive care management platform</p>
        
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="text-xl font-semibold mb-2">Bookings</h3>
            <p className="text-slate-600">Manage appointments and schedules efficiently</p>
          </div>
          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="text-xl font-semibold mb-2">Inbox</h3>
            <p className="text-slate-600">Centralized communication hub</p>
          </div>
          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="text-xl font-semibold mb-2">Contacts</h3>
            <p className="text-slate-600">Manage clients and staff information</p>
          </div>
          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="text-xl font-semibold mb-2">Inventory</h3>
            <p className="text-slate-600">Track supplies and equipment</p>
          </div>
          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="text-xl font-semibold mb-2">Services</h3>
            <p className="text-slate-600">Define and manage care services</p>
          </div>
          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="text-xl font-semibold mb-2">Forms</h3>
            <p className="text-slate-600">Custom forms and data collection</p>
          </div>
        </div>
      </div>
    </div>
  )
}
