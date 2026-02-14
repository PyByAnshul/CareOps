'use client'

import { useState } from 'react'
import { Mail, Send, CheckCircle, AlertCircle, Video } from 'lucide-react'
import { apiClient } from '@/core/api/client'

export default function IntegrationsPage() {
  const [testEmail, setTestEmail] = useState('')
  const [sending, setSending] = useState(false)
  const [result, setResult] = useState<{ success: boolean; message: string } | null>(null)
  const [webexToken, setWebexToken] = useState('')
  const [savingWebex, setSavingWebex] = useState(false)
  const [webexResult, setWebexResult] = useState<{ success: boolean; message: string } | null>(null)

  const handleTestEmail = async (e: React.FormEvent) => {
    e.preventDefault()
    setSending(true)
    setResult(null)

    try {
      await apiClient.post('/api/integrations/email/test', {
        to_email: testEmail,
        subject: 'Test Email from CareOps',
        body: 'This is a test email to verify your email integration is working correctly.'
      })
      setResult({ success: true, message: 'Test email sent successfully!' })
      setTestEmail('')
    } catch (error: any) {
      setResult({ 
        success: false, 
        message: error.response?.data?.detail || 'Failed to send test email. Please check your email configuration.' 
      })
    } finally {
      setSending(false)
    }
  }

  const handleSaveWebex = async (e: React.FormEvent) => {
    e.preventDefault()
    setSavingWebex(true)
    setWebexResult(null)

    try {
      await apiClient.post('/api/integrations', {
        integration_type: 'webex',
        provider: 'webex',
        config: {
          access_token: webexToken
        }
      })
      setWebexResult({ success: true, message: 'Webex integration saved successfully!' })
    } catch (error: any) {
      setWebexResult({ 
        success: false, 
        message: error.response?.data?.detail || 'Failed to save Webex configuration.' 
      })
    } finally {
      setSavingWebex(false)
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-slate-900">Integrations</h1>
        <p className="text-slate-600 mt-1">Connect external services to extend CareOps functionality</p>
      </div>

      {/* Email Integration */}
      <div className="bg-white rounded-lg border border-slate-200 p-6">
        <div className="flex items-center gap-3 mb-4">
          <div className="p-3 bg-blue-100 rounded-lg">
            <Mail className="w-6 h-6 text-blue-600" />
          </div>
          <div>
            <h2 className="text-xl font-semibold text-slate-900">Email Integration</h2>
            <p className="text-sm text-slate-600">Send automated emails for bookings and notifications</p>
          </div>
        </div>

        <div className="space-y-4">
          <div className="p-4 bg-slate-50 rounded-lg">
            <h3 className="font-medium text-slate-900 mb-2">Current Configuration</h3>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-slate-600">Provider:</span>
                <span className="font-medium text-slate-900">SMTP (Default)</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-600">Status:</span>
                <span className="flex items-center gap-1 text-green-600">
                  <CheckCircle className="w-4 h-4" />
                  Active
                </span>
              </div>
            </div>
          </div>

          <div>
            <h3 className="font-medium text-slate-900 mb-3">Test Email Integration</h3>
            <form onSubmit={handleTestEmail} className="space-y-3">
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">
                  Send test email to:
                </label>
                <input
                  type="email"
                  value={testEmail}
                  onChange={(e) => setTestEmail(e.target.value)}
                  placeholder="your.email@example.com"
                  required
                  className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
              <button
                type="submit"
                disabled={sending}
                className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 disabled:bg-slate-400 text-white px-4 py-2 rounded-lg transition-colors"
              >
                <Send className="w-4 h-4" />
                {sending ? 'Sending...' : 'Send Test Email'}
              </button>
            </form>

            {result && (
              <div className={`mt-4 p-4 rounded-lg flex items-start gap-3 ${
                result.success ? 'bg-green-50 border border-green-200' : 'bg-red-50 border border-red-200'
              }`}>
                {result.success ? (
                  <CheckCircle className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
                ) : (
                  <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
                )}
                <div>
                  <p className={`font-medium ${
                    result.success ? 'text-green-900' : 'text-red-900'
                  }`}>
                    {result.success ? 'Success!' : 'Error'}
                  </p>
                  <p className={`text-sm ${
                    result.success ? 'text-green-700' : 'text-red-700'
                  }`}>
                    {result.message}
                  </p>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Webex Integration */}
      <div className="bg-white rounded-lg border border-slate-200 p-6">
        <div className="flex items-center gap-3 mb-4">
          <div className="p-3 bg-purple-100 rounded-lg">
            <Video className="w-6 h-6 text-purple-600" />
          </div>
          <div>
            <h2 className="text-xl font-semibold text-slate-900">Webex Meetings</h2>
            <p className="text-sm text-slate-600">Automatically create video meetings for confirmed bookings</p>
          </div>
        </div>

        <div className="space-y-4">
          <div className="p-4 bg-amber-50 border border-amber-200 rounded-lg">
            <p className="text-sm text-amber-800">
              <strong>Setup Instructions:</strong>
              <ol className="list-decimal ml-4 mt-2 space-y-1">
                <li>Go to <a href="https://developer.webex.com/my-apps" target="_blank" className="underline font-medium">Webex Developer Portal</a></li>
                <li>Click "Create a New App" → "Create an Integration"</li>
                <li>Fill in: Name="CareOps", Redirect URI=<code className="bg-amber-100 px-1 rounded">http://localhost:3000</code></li>
                <li>Select scopes: <code className="bg-amber-100 px-1 rounded">meeting:schedules_write</code> and <code className="bg-amber-100 px-1 rounded">meeting:schedules_read</code></li>
                <li>Click "Add Integration"</li>
                <li>Scroll down to find <strong>"Your Access Token"</strong> section (NOT Client ID/Secret)</li>
                <li>Click "Copy" to copy the access token (long string starting with letters/numbers)</li>
                <li>Paste the token below and save</li>
              </ol>
              <p className="mt-3 text-xs">
                <strong>Note:</strong> Token expires after 12 hours. Return to Developer Portal and click "Regenerate Access Token" to get a new one.
              </p>
            </p>
          </div>

          <form onSubmit={handleSaveWebex} className="space-y-3">
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">
                Webex Access Token
              </label>
              <input
                type="password"
                value={webexToken}
                onChange={(e) => setWebexToken(e.target.value)}
                placeholder="Enter your Webex access token"
                required
                className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              />
            </div>
            <button
              type="submit"
              disabled={savingWebex}
              className="flex items-center gap-2 bg-purple-600 hover:bg-purple-700 disabled:bg-slate-400 text-white px-4 py-2 rounded-lg transition-colors"
            >
              <Video className="w-4 h-4" />
              {savingWebex ? 'Saving...' : 'Save Webex Configuration'}
            </button>
          </form>

          {webexResult && (
            <div className={`mt-4 p-4 rounded-lg flex items-start gap-3 ${
              webexResult.success ? 'bg-green-50 border border-green-200' : 'bg-red-50 border border-red-200'
            }`}>
              {webexResult.success ? (
                <CheckCircle className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
              ) : (
                <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
              )}
              <div>
                <p className={`font-medium ${
                  webexResult.success ? 'text-green-900' : 'text-red-900'
                }`}>
                  {webexResult.success ? 'Success!' : 'Error'}
                </p>
                <p className={`text-sm ${
                  webexResult.success ? 'text-green-700' : 'text-red-700'
                }`}>
                  {webexResult.message}
                </p>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Coming Soon Integrations */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {[
          { name: 'SMS Notifications', icon: '📱', description: 'Send SMS reminders via Twilio', status: 'Coming Soon' },
          { name: 'Payment Processing', icon: '💳', description: 'Accept payments with Stripe', status: 'Coming Soon' },
          { name: 'Calendar Sync', icon: '📅', description: 'Sync with Google Calendar', status: 'Coming Soon' },
          { name: 'CRM Integration', icon: '🤝', description: 'Connect with Salesforce', status: 'Coming Soon' },
          { name: 'Analytics', icon: '📊', description: 'Track with Google Analytics', status: 'Coming Soon' },
          { name: 'Webhooks', icon: '🔗', description: 'Custom webhook integrations', status: 'Coming Soon' },
        ].map((integration, idx) => (
          <div key={idx} className="bg-white rounded-lg border border-slate-200 p-6 opacity-60">
            <div className="text-4xl mb-3">{integration.icon}</div>
            <h3 className="font-semibold text-slate-900 mb-1">{integration.name}</h3>
            <p className="text-sm text-slate-600 mb-3">{integration.description}</p>
            <span className="inline-block px-3 py-1 bg-slate-100 text-slate-600 text-xs font-medium rounded-full">
              {integration.status}
            </span>
          </div>
        ))}
      </div>
    </div>
  )
}
