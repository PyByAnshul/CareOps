import { ContactForm } from '@/features/contacts/components/ContactForm'

export default function NewContactPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-slate-900">New Contact</h1>
        <p className="text-slate-600 mt-1">Create a new contact</p>
      </div>

      <div className="bg-white rounded-lg border border-slate-200 p-6">
        <ContactForm />
      </div>
    </div>
  )
}
