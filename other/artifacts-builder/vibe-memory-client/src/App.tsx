import React, { useState, useEffect } from 'react';
import { 
  Folder, FileText, GitBranch, Cloud, CheckCircle, AlertCircle, 
  Upload, Download, RefreshCw, Save, Clock, Shield, HardDrive,
  ChevronRight, ChevronDown, FileCode, Database, Settings,
  Workflow, MessageSquare, ArrowRightLeft, GitCommit, Terminal
} from 'lucide-react';
import './App.css';

// Types
interface MemoryFile {
  id: string;
  name: string;
  path: string;
  type: 'file' | 'folder';
  content?: string;
  lastModified: Date;
  syncStatus: 'synced' | 'pending' | 'conflict' | 'local-only';
  size: string;
}

interface GitCommit {
  hash: string;
  message: string;
  author: string;
  date: Date;
  filesChanged: number;
}

interface SyncStatus {
  lastSync: Date | null;
  status: 'idle' | 'syncing' | 'error' | 'offline';
  pendingChanges: number;
  remoteUrl: string;
}

// Mock Data
const MOCK_FILES: MemoryFile[] = [
  {
    id: '1',
    name: 'persona.md',
    path: '/persona.md',
    type: 'file',
    content: `# Agent Persona

**Name:** VibeNative Assistant
**Role:** Multi-agent orchestration specialist
**Tone:** Friendly, proactive, technically precise

## Core Behaviors
- Remembers user preferences across sessions
- Proactively offers architectural suggestions
- Always asks before making destructive changes

## Communication Style
- Uses casual but professional language
- Explains complex concepts simply
- Celebrates wins with emoji 🎉`,
    lastModified: new Date('2026-02-15T10:30:00'),
    syncStatus: 'synced',
    size: '245 bytes'
  },
  {
    id: '2',
    name: 'human.md',
    path: '/human.md',
    type: 'file',
    content: `# User Profile

**Name:** Clayton
**Role:** Founder, Donjon Agency
**Timezone:** America/Chicago

## Preferences
- Prefers detailed explanations with examples
- Likes to understand the "why" behind decisions
- Enjoys brainstorming sessions
- Default model: kimi-2.5 (cost-effective)

## Active Projects
- Vibe Native (ServicePro v2)
- Agent memory system architecture
- Fundraising deck preparation

## Fun Facts
- Enjoys OSRS in downtime
- Prefers buttermilk biscuits 🍪`,
    lastModified: new Date('2026-02-15T14:20:00'),
    syncStatus: 'pending',
    size: '312 bytes'
  },
  {
    id: '3',
    name: 'context',
    path: '/context',
    type: 'folder',
    lastModified: new Date('2026-02-15T09:00:00'),
    syncStatus: 'synced',
    size: '--'
  },
  {
    id: '4',
    name: 'projects.md',
    path: '/context/projects.md',
    type: 'file',
    content: `# Active Projects

## Vibe Native (Primary)
Status: In Development
Stack: Next.js, Supabase, Stack Auth, E2B

### Current Sprint
- Local-first memory architecture
- Git-backed agent persistence
- Multi-tenant agent docking

## Donjon Agency Website
Status: Maintenance
Last Updated: 2026-01-20

## Consulting Projects
- Knowledge Vault (completed)
- ROI Calculator (deployed)`,
    lastModified: new Date('2026-02-15T16:45:00'),
    syncStatus: 'pending',
    size: '278 bytes'
  },
  {
    id: '5',
    name: 'tech.md',
    path: '/context/tech.md',
    type: 'file',
    content: `# Tech Stack

## Frontend
- Next.js 15 (App Router)
- React 19
- TypeScript 5.3
- Tailwind CSS
- shadcn/ui

## Backend
- Supabase (PostgreSQL)
- Stack Auth
- E2B Sandboxes

## AI/ML
- Letta (memory)
- OpenAI GPT-4o
- Codex 5.2/5.3

## Infrastructure
- Vercel (hosting)
- GitHub (repo)
- Gitea (memory repos)`,
    lastModified: new Date('2026-02-14T11:00:00'),
    syncStatus: 'synced',
    size: '198 bytes'
  },
  {
    id: '6',
    name: 'work',
    path: '/work',
    type: 'folder',
    lastModified: new Date('2026-02-15T08:00:00'),
    syncStatus: 'synced',
    size: '--'
  },
  {
    id: '7',
    name: 'active.md',
    path: '/work/active.md',
    type: 'file',
    content: `# Current Task

**Status:** In Progress
**Started:** 2026-02-15 17:00
**Priority:** High

## Task
Design and prototype local-first memory architecture for Vibe Native agents.

## Progress
✅ Conceptual architecture complete
✅ Git sync strategy defined
🔄 Building UI prototype (current)
⏳ Implementation planning

## Blockers
None currently.

## Next Steps
1. Create interactive demo
2. Present to user
3. Gather feedback
4. Begin implementation`,
    lastModified: new Date('2026-02-15T17:30:00'),
    syncStatus: 'local-only',
    size: '356 bytes'
  }
];

const MOCK_COMMITS: GitCommit[] = [
  {
    hash: 'a1b2c3d',
    message: 'Update active task with architecture design',
    author: 'VibeNative Agent',
    date: new Date('2026-02-15T17:30:00'),
    filesChanged: 1
  },
  {
    hash: 'e4f5g6h',
    message: 'Update human.md with current preferences',
    author: 'VibeNative Agent',
    date: new Date('2026-02-15T14:20:00'),
    filesChanged: 1
  },
  {
    hash: 'i7j8k9l',
    message: 'Add tech stack documentation',
    author: 'VibeNative Agent',
    date: new Date('2026-02-14T11:00:00'),
    filesChanged: 3
  },
  {
    hash: 'm0n1o2p',
    message: 'Initial memory structure setup',
    author: 'System',
    date: new Date('2026-02-14T09:00:00'),
    filesChanged: 7
  }
];

// Components
const FileIcon = ({ name, type }: { name: string; type: string }) => {
  if (type === 'folder') return <Folder className="w-4 h-4 text-yellow-500" />;
  if (name.endsWith('.md')) return <FileText className="w-4 h-4 text-blue-500" />;
  if (name.endsWith('.json')) return <FileCode className="w-4 h-4 text-green-500" />;
  return <FileText className="w-4 h-4 text-gray-500" />;
};

const StatusBadge = ({ status }: { status: MemoryFile['syncStatus'] }) => {
  const styles = {
    'synced': 'bg-green-100 text-green-700 border-green-300',
    'pending': 'bg-yellow-100 text-yellow-700 border-yellow-300',
    'conflict': 'bg-red-100 text-red-700 border-red-300',
    'local-only': 'bg-gray-100 text-gray-700 border-gray-300'
  };
  
  const labels = {
    'synced': 'Synced',
    'pending': 'Pending',
    'conflict': 'Conflict',
    'local-only': 'Local'
  };
  
  return (
    <span className={`px-2 py-0.5 text-xs rounded-full border ${styles[status]}`}>
      {labels[status]}
    </span>
  );
};

const SyncIndicator = ({ status, lastSync }: SyncStatus) => {
  const getIcon = () => {
    switch (status) {
      case 'syncing':
        return <RefreshCw className="w-5 h-5 text-blue-500 animate-spin" />;
      case 'error':
        return <AlertCircle className="w-5 h-5 text-red-500" />;
      case 'offline':
        return <Cloud className="w-5 h-5 text-gray-400" />;
      default:
        return <CheckCircle className="w-5 h-5 text-green-500" />;
    }
  };
  
  return (
    <div className="flex items-center gap-2">
      {getIcon()}
      <div className="flex flex-col">
        <span className="text-sm font-medium capitalize">{status}</span>
        {lastSync && (
          <span className="text-xs text-gray-500">
            Last sync: {lastSync.toLocaleTimeString()}
          </span>
        )}
      </div>
    </div>
  );
};

export default function App() {
  const [selectedFile, setSelectedFile] = useState<MemoryFile | null>(null);
  const [expandedFolders, setExpandedFolders] = useState<Set<string>>(new Set(['3', '6']));
  const [syncStatus, setSyncStatus] = useState<SyncStatus>({
    lastSync: new Date('2026-02-15T16:00:00'),
    status: 'idle',
    pendingChanges: 2,
    remoteUrl: 'git.vibe-native.io/clayton/agent-memory'
  });
  const [activeTab, setActiveTab] = useState<'files' | 'git' | 'sync' | 'bridge'>('files');
  const [fileContent, setFileContent] = useState<string>('');
  const [isEditing, setIsEditing] = useState(false);
  
  useEffect(() => {
    if (selectedFile?.content) {
      setFileContent(selectedFile.content);
    }
  }, [selectedFile]);
  
  const toggleFolder = (id: string) => {
    const newExpanded = new Set(expandedFolders);
    if (newExpanded.has(id)) {
      newExpanded.delete(id);
    } else {
      newExpanded.add(id);
    }
    setExpandedFolders(newExpanded);
  };
  
  const handleSync = () => {
    setSyncStatus(prev => ({ ...prev, status: 'syncing' }));
    setTimeout(() => {
      setSyncStatus(prev => ({
        ...prev,
        status: 'idle',
        lastSync: new Date(),
        pendingChanges: 0
      }));
    }, 2000);
  };
  
  const renderFileTree = (files: MemoryFile[], parentPath: string = '') => {
    return files
      .filter(file => {
        if (parentPath === '') return !file.path.includes('/', 1);
        const relativePath = file.path.replace(parentPath + '/', '');
        return file.path.startsWith(parentPath + '/') && 
               !relativePath.includes('/', relativePath.indexOf('/') + 1);
      })
      .map(file => (
        <div key={file.id}>
          <div
            className={`flex items-center gap-2 p-2 rounded cursor-pointer hover:bg-gray-100 ${
              selectedFile?.id === file.id ? 'bg-blue-50 border-l-4 border-blue-500' : ''
            }`}
            onClick={() => file.type === 'folder' ? toggleFolder(file.id) : setSelectedFile(file)}
          >
            {file.type === 'folder' && (
              expandedFolders.has(file.id) ? 
                <ChevronDown className="w-4 h-4 text-gray-400" /> : 
                <ChevronRight className="w-4 h-4 text-gray-400" />
            )}
            <FileIcon name={file.name} type={file.type} />
            <span className="flex-1 text-sm">{file.name}</span>
            {file.type === 'file' && <StatusBadge status={file.syncStatus} />}
          </div>
          {file.type === 'folder' && expandedFolders.has(file.id) && (
            <div className="ml-6">
              {renderFileTree(MOCK_FILES, file.path)}
            </div>
          )}
        </div>
      ));
  };
  
  return (
    <div className="min-h-screen bg-gray-50 p-6">
      {/* Header */}
      <header className="mb-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Vibe Memory Client</h1>
            <p className="text-gray-600 mt-1">Local-first agent memory with git sync</p>
          </div>
          <div className="flex items-center gap-4">
            <SyncIndicator {...syncStatus} />
            <button 
              onClick={handleSync}
              disabled={syncStatus.status === 'syncing'}
              className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
            >
              <RefreshCw className={`w-4 h-4 ${syncStatus.status === 'syncing' ? 'animate-spin' : ''}`} />
              Sync Now
            </button>
          </div>
        </div>
      </header>
      
      {/* Architecture Overview */}
      <div className="grid grid-cols-3 gap-4 mb-6">
        <div className="bg-white p-4 rounded-lg shadow-sm border">
          <div className="flex items-center gap-3 mb-2">
            <HardDrive className="w-5 h-5 text-blue-500" />
            <h3 className="font-semibold">Local Storage</h3>
          </div>
          <p className="text-sm text-gray-600">~/vibe-native-memory/</p>
          <p className="text-xs text-gray-500 mt-1">7 files • 1.4 KB</p>
        </div>
        <div className="bg-white p-4 rounded-lg shadow-sm border">
          <div className="flex items-center gap-3 mb-2">
            <GitBranch className="w-5 h-5 text-orange-500" />
            <h3 className="font-semibold">Git Repository</h3>
          </div>
          <p className="text-sm text-gray-600">main branch</p>
          <p className="text-xs text-gray-500 mt-1">4 commits • 2 pending</p>
        </div>
        <div className="bg-white p-4 rounded-lg shadow-sm border">
          <div className="flex items-center gap-3 mb-2">
            <Cloud className="w-5 h-5 text-purple-500" />
            <h3 className="font-semibold">Remote Sync</h3>
          </div>
          <p className="text-sm text-gray-600 truncate">{syncStatus.remoteUrl}</p>
          <p className="text-xs text-gray-500 mt-1">
            {syncStatus.pendingChanges} changes pending
          </p>
        </div>
      </div>
      
      {/* Main Content */}
      <div className="grid grid-cols-12 gap-6">
        {/* Sidebar */}
        <div className="col-span-4 bg-white rounded-lg shadow-sm border overflow-hidden">
          {/* Tabs */}
          <div className="flex border-b">
            {(['files', 'git', 'sync', 'bridge'] as const).map(tab => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`flex-1 py-3 text-sm font-medium capitalize ${
                  activeTab === tab 
                    ? 'text-blue-600 border-b-2 border-blue-600 bg-blue-50' 
                    : 'text-gray-600 hover:bg-gray-50'
                }`}
              >
                {tab === 'files' && <Folder className="w-4 h-4 inline mr-2" />}
                {tab === 'git' && <GitBranch className="w-4 h-4 inline mr-2" />}
                {tab === 'sync' && <RefreshCw className="w-4 h-4 inline mr-2" />}
                {tab === 'bridge' && <Workflow className="w-4 h-4 inline mr-2" />}
                {tab}
              </button>
            ))}
          </div>
          
          {/* Tab Content */}
          <div className="p-4 h-96 overflow-auto">
            {activeTab === 'files' && (
              <div>
                <div className="flex items-center gap-2 mb-4 pb-2 border-b">
                  <Database className="w-4 h-4 text-gray-400" />
                  <span className="text-sm font-medium text-gray-700">Memory Files</span>
                </div>
                {renderFileTree(MOCK_FILES)}
              </div>
            )}
            
            {activeTab === 'git' && (
              <div>
                <div className="flex items-center justify-between mb-4 pb-2 border-b">
                  <span className="text-sm font-medium text-gray-700">Recent Commits</span>
                  <span className="text-xs text-gray-500">4 total</span>
                </div>
                <div className="space-y-3">
                  {MOCK_COMMITS.map(commit => (
                    <div key={commit.hash} className="p-3 bg-gray-50 rounded text-sm">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="font-mono text-xs text-gray-500">{commit.hash}</span>
                        <span className="text-xs text-gray-400">
                          {commit.date.toLocaleDateString()}
                        </span>
                      </div>
                      <p className="text-gray-800">{commit.message}</p>
                      <p className="text-xs text-gray-500 mt-1">
                        {commit.filesChanged} file{commit.filesChanged > 1 ? 's' : ''} changed
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            )}
            
            {activeTab === 'sync' && (
              <div className="space-y-4">
                <div className="p-4 bg-blue-50 rounded-lg border border-blue-200">
                  <h4 className="font-medium text-blue-900 mb-2">Sync Status</h4>
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span className="text-blue-700">Status:</span>
                      <span className="capitalize text-blue-900">{syncStatus.status}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-blue-700">Pending:</span>
                      <span className="text-blue-900">{syncStatus.pendingChanges} changes</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-blue-700">Remote:</span>
                      <span className="text-blue-900 text-xs">{syncStatus.remoteUrl}</span>
                    </div>
                  </div>
                </div>
                
                <div className="p-4 bg-yellow-50 rounded-lg border border-yellow-200">
                  <h4 className="font-medium text-yellow-900 mb-2">Pending Changes</h4>
                  <ul className="text-sm space-y-1">
                    <li className="flex items-center gap-2">
                      <Upload className="w-3 h-3 text-yellow-600" />
                      <span className="text-yellow-800">human.md (modified)</span>
                    </li>
                    <li className="flex items-center gap-2">
                      <Upload className="w-3 h-3 text-yellow-600" />
                      <span className="text-yellow-800">context/projects.md (modified)</span>
                    </li>
                  </ul>
                </div>
              </div>
            )}
            
            {activeTab === 'bridge' && (
              <div className="space-y-4">
                <div className="p-4 bg-indigo-50 rounded-lg border border-indigo-200">
                  <div className="flex items-center gap-2 mb-3">
                    <Workflow className="w-5 h-5 text-indigo-600" />
                    <h4 className="font-medium text-indigo-900">Letta Memory Bridge</h4>
                  </div>
                  <p className="text-sm text-indigo-700 mb-3">
                    Create a bridge module to sync Vibe Native conversations with Letta memory format.
                  </p>
                  <div className="text-xs text-indigo-600 bg-white p-2 rounded border border-indigo-200 font-mono">
                    app/lib/letta-bridge.ts
                  </div>
                </div>
                
                <div className="p-4 bg-white rounded-lg border">
                  <h5 className="font-medium text-gray-900 mb-3 flex items-center gap-2">
                    <GitCommit className="w-4 h-4 text-orange-500" />
                    Git Operations
                  </h5>
                  <ul className="text-sm space-y-2 text-gray-700">
                    <li className="flex items-start gap-2">
                      <CheckCircle className="w-4 h-4 text-green-500 mt-0.5" />
                      <span>Auto-commit conversation changes</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <CheckCircle className="w-4 h-4 text-green-500 mt-0.5" />
                      <span>Push to remote repository</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <CheckCircle className="w-4 h-4 text-green-500 mt-0.5" />
                      <span>Pull latest memory updates</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <CheckCircle className="w-4 h-4 text-green-500 mt-0.5" />
                      <span>Handle merge conflicts</span>
                    </li>
                  </ul>
                </div>
                
                <div className="p-4 bg-white rounded-lg border">
                  <h5 className="font-medium text-gray-900 mb-3 flex items-center gap-2">
                    <ArrowRightLeft className="w-4 h-4 text-blue-500" />
                    Format Conversion
                  </h5>
                  <ul className="text-sm space-y-2 text-gray-700">
                    <li className="flex items-start gap-2">
                      <MessageSquare className="w-4 h-4 text-blue-500 mt-0.5" />
                      <span>Convert Vibe Native conversations → Letta format</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <Database className="w-4 h-4 text-blue-500 mt-0.5" />
                      <span>Extract entities and observations</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <FileText className="w-4 h-4 text-blue-500 mt-0.5" />
                      <span>Update persona.md and human.md</span>
                    </li>
                  </ul>
                </div>
                
                <div className="p-4 bg-gray-50 rounded-lg border border-gray-200">
                  <h5 className="font-medium text-gray-900 mb-2 flex items-center gap-2">
                    <Terminal className="w-4 h-4 text-gray-600" />
                    Quick Start
                  </h5>
                  <div className="text-xs text-gray-600 bg-gray-900 text-gray-100 p-3 rounded font-mono">
{`// Initialize the bridge
const bridge = new LettaBridge({
  userId: 'clayton',
  agentId: 'dondog',
  repoPath: '~/.vibe-native-memory'
});

// Sync conversation to memory
await bridge.syncConversation(conversation);

// Push to remote
await bridge.pushToRemote();`}
                  </div>
                </div>
                
                <button className="w-full flex items-center justify-center gap-2 px-4 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 font-medium">
                  <Workflow className="w-4 h-4" />
                  Create Bridge Module
                </button>
              </div>
            )}
          </div>
        </div>
        
        {/* File Viewer */}
        <div className="col-span-8 bg-white rounded-lg shadow-sm border overflow-hidden">
          {selectedFile ? (
            <div className="h-full flex flex-col">
              {/* File Header */}
              <div className="flex items-center justify-between p-4 border-b bg-gray-50">
                <div className="flex items-center gap-3">
                  <FileIcon name={selectedFile.name} type={selectedFile.type} />
                  <div>
                    <h3 className="font-semibold text-gray-900">{selectedFile.name}</h3>
                    <p className="text-xs text-gray-500">
                      {selectedFile.path} • {selectedFile.size} • 
                      Modified {selectedFile.lastModified.toLocaleString()}
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <StatusBadge status={selectedFile.syncStatus} />
                  <button
                    onClick={() => setIsEditing(!isEditing)}
                    className="flex items-center gap-1 px-3 py-1.5 text-sm border rounded hover:bg-gray-50"
                  >
                    {isEditing ? <CheckCircle className="w-4 h-4" /> : <Settings className="w-4 h-4" />}
                    {isEditing ? 'Done' : 'Edit'}
                  </button>
                  {isEditing && (
                    <button className="flex items-center gap-1 px-3 py-1.5 text-sm bg-blue-600 text-white rounded hover:bg-blue-700">
                      <Save className="w-4 h-4" />
                      Save
                    </button>
                  )}
                </div>
              </div>
              
              {/* File Content */}
              <div className="flex-1 p-4 overflow-auto">
                {isEditing ? (
                  <textarea
                    value={fileContent}
                    onChange={(e) => setFileContent(e.target.value)}
                    className="w-full h-full p-4 font-mono text-sm bg-gray-50 rounded border resize-none focus:outline-none focus:ring-2 focus:ring-blue-500"
                    spellCheck={false}
                  />
                ) : (
                  <pre className="font-mono text-sm whitespace-pre-wrap">
                    {selectedFile.content}
                  </pre>
                )}
              </div>
            </div>
          ) : (
            <div className="h-full flex items-center justify-center text-gray-400">
              <div className="text-center">
                <FileText className="w-12 h-12 mx-auto mb-3 opacity-50" />
                <p>Select a file to view its contents</p>
              </div>
            </div>
          )}
        </div>
      </div>
      
      {/* Footer */}
      <footer className="mt-6 p-4 bg-white rounded-lg shadow-sm border">
        <div className="flex items-center justify-between text-sm text-gray-600">
          <div className="flex items-center gap-4">
            <span className="flex items-center gap-1">
              <Shield className="w-4 h-4 text-green-500" />
              End-to-end encrypted
            </span>
            <span className="flex items-center gap-1">
              <Clock className="w-4 h-4 text-blue-500" />
              Auto-sync enabled
            </span>
          </div>
          <div className="flex items-center gap-4">
            <span>7 files tracked</span>
            <span>Last backup: 2 minutes ago</span>
          </div>
        </div>
      </footer>
    </div>
  );
}
