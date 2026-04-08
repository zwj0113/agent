'use client'

import { useState } from 'react'

type Tab = 'models' | 'skills' | 'mcp' | 'users'

export default function AdminDashboard() {
  const [activeTab, setActiveTab] = useState<Tab>('models')

  return (
    <div className="min-h-screen bg-background">
      {/* Sidebar */}
      <div className="flex">
        <aside className="w-64 bg-surface border-r border-border min-h-screen p-4">
          <h2 className="text-lg font-semibold text-primary mb-6">Admin</h2>
          <nav className="space-y-2">
            {[
              { id: 'models', label: 'Model Config', icon: '🤖' },
              { id: 'skills', label: 'Skills', icon: '🛠️' },
              { id: 'mcp', label: 'MCP Servers', icon: '🔌' },
              { id: 'users', label: 'Users', icon: '👥' },
            ].map(item => (
              <button
                key={item.id}
                onClick={() => setActiveTab(item.id as Tab)}
                className={`w-full text-left px-4 py-2 rounded-lg transition-colors ${
                  activeTab === item.id
                    ? 'bg-primary/20 text-primary'
                    : 'text-gray-400 hover:bg-gray-800'
                }`}
              >
                <span className="mr-2">{item.icon}</span>
                {item.label}
              </button>
            ))}
          </nav>
        </aside>

        {/* Main Content */}
        <main className="flex-1 p-8">
          <h1 className="text-2xl font-bold mb-6">
            {activeTab === 'models' && 'Model Configuration'}
            {activeTab === 'skills' && 'Skill Management'}
            {activeTab === 'mcp' && 'MCP Servers'}
            {activeTab === 'users' && 'User Management'}
          </h1>

          {/* Model Config Tab */}
          {activeTab === 'models' && (
            <div className="space-y-6">
              <div className="bg-surface border border-border rounded-lg p-6">
                <h3 className="text-lg font-medium mb-4">API Keys</h3>
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm text-gray-400 mb-2">OpenAI API Key</label>
                    <input
                      type="password"
                      placeholder="sk-..."
                      className="w-full bg-background border border-border rounded-lg px-4 py-2 text-white"
                    />
                  </div>
                  <div>
                    <label className="block text-sm text-gray-400 mb-2">Default Model</label>
                    <select className="w-full bg-background border border-border rounded-lg px-4 py-2 text-white">
                      <option value="gpt-4o-mini">GPT-4o Mini</option>
                      <option value="gpt-4o">GPT-4o</option>
                      <option value="gpt-3.5-turbo">GPT-3.5 Turbo</option>
                    </select>
                  </div>
                  <button className="bg-primary hover:bg-primary/90 text-black font-medium px-4 py-2 rounded-lg">
                    Save Configuration
                  </button>
                </div>
              </div>

              <div className="bg-surface border border-border rounded-lg p-6">
                <h3 className="text-lg font-medium mb-4">Token Usage</h3>
                <div className="grid grid-cols-3 gap-4">
                  <div className="bg-background rounded-lg p-4">
                    <p className="text-gray-400 text-sm">Today</p>
                    <p className="text-2xl font-bold text-primary">1,234</p>
                  </div>
                  <div className="bg-background rounded-lg p-4">
                    <p className="text-gray-400 text-sm">This Week</p>
                    <p className="text-2xl font-bold text-primary">8,901</p>
                  </div>
                  <div className="bg-background rounded-lg p-4">
                    <p className="text-gray-400 text-sm">This Month</p>
                    <p className="text-2xl font-bold text-primary">45,678</p>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Skills Tab */}
          {activeTab === 'skills' && (
            <div className="space-y-6">
              <div className="bg-surface border border-border rounded-lg p-6">
                <div className="flex justify-between items-center mb-4">
                  <h3 className="text-lg font-medium">Installed Skills</h3>
                  <button className="bg-primary hover:bg-primary/90 text-black font-medium px-4 py-2 rounded-lg">
                    Upload Skill
                  </button>
                </div>
                <div className="space-y-2">
                  {[
                    { name: 'calculator', desc: 'Mathematical expression evaluator', enabled: true },
                    { name: 'get_weather', desc: 'Weather information lookup', enabled: true },
                  ].map(skill => (
                    <div key={skill.name} className="flex justify-between items-center bg-background rounded-lg p-4">
                      <div>
                        <p className="font-medium">{skill.name}</p>
                        <p className="text-sm text-gray-400">{skill.desc}</p>
                      </div>
                      <div className="flex items-center gap-4">
                        <label className="relative inline-flex items-center cursor-pointer">
                          <input type="checkbox" checked={skill.enabled} className="sr-only peer" />
                          <div className="w-11 h-6 bg-gray-700 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary"></div>
                        </label>
                        <button className="text-red-400 hover:text-red-300">Uninstall</button>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* MCP Tab */}
          {activeTab === 'mcp' && (
            <div className="space-y-6">
              <div className="bg-surface border border-border rounded-lg p-6">
                <div className="flex justify-between items-center mb-4">
                  <h3 className="text-lg font-medium">MCP Servers</h3>
                  <button className="bg-primary hover:bg-primary/90 text-black font-medium px-4 py-2 rounded-lg">
                    Add Server
                  </button>
                </div>
                <p className="text-gray-400 text-sm">No MCP servers configured.</p>
              </div>
            </div>
          )}

          {/* Users Tab */}
          {activeTab === 'users' && (
            <div className="space-y-6">
              <div className="bg-surface border border-border rounded-lg p-6">
                <div className="flex justify-between items-center mb-4">
                  <h3 className="text-lg font-medium">Users</h3>
                  <button className="bg-primary hover:bg-primary/90 text-black font-medium px-4 py-2 rounded-lg">
                    Add User
                  </button>
                </div>
                <div className="space-y-2">
                  {[
                    { name: 'Admin', email: 'admin@example.com', role: 'admin' },
                    { name: 'User', email: 'user@example.com', role: 'user' },
                  ].map(user => (
                    <div key={user.email} className="flex justify-between items-center bg-background rounded-lg p-4">
                      <div>
                        <p className="font-medium">{user.name}</p>
                        <p className="text-sm text-gray-400">{user.email}</p>
                      </div>
                      <span className="text-xs px-2 py-1 bg-gray-700 rounded">{user.role}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
        </main>
      </div>
    </div>
  )
}
