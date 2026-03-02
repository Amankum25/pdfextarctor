import React, { useState, useEffect, useRef } from 'react';
import { Send, Upload, FileText, Loader2, Bot, User, CheckCircle, AlertCircle, Sparkles, HelpCircle, Files } from 'lucide-react';
import { uploadFiles, askQuestion, getHealth, getSuggestedQuestions } from './api';
import clsx from 'clsx';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [systemReady, setSystemReady] = useState(false);
  const [uploadStatus, setUploadStatus] = useState(null);
  const [suggestedQuestions, setSuggestedQuestions] = useState([]);
  const [loadingSuggestions, setLoadingSuggestions] = useState(false);
  const [errorMsg, setErrorMsg] = useState(null);
  const [fileInputKey, setFileInputKey] = useState(Date.now());

  const messagesEndRef = useRef(null);

  // Clear error after 5 seconds
  useEffect(() => {
    if (errorMsg) {
      const timer = setTimeout(() => setErrorMsg(null), 5000);
      return () => clearTimeout(timer);
    }
  }, [errorMsg]);

  useEffect(() => {
    checkSystemStatus();
    setMessages([{
      role: 'assistant',
      content: 'Hello! I am your **Insurance Policy Auditor**. Upload your policy document, and I will help you uncover hidden risks, exclusions, and financial limits.',
      sources: []
    }]);
  }, []);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const checkSystemStatus = async () => {
    try {
      const status = await getHealth();
      setSystemReady(status.ready);
    } catch (e) {
      console.error("System check failed", e);
    }
  };

  const fetchSuggestedQuestions = async () => {
    setLoadingSuggestions(true);
    try {
      const data = await getSuggestedQuestions();
      const fetchedQs = data.questions || [];
      // Always prepend the summary option if not present
      const completeQs = ['Give me a summary of this document', ...fetchedQs.filter(q => !q.toLowerCase().includes('summary'))];
      setSuggestedQuestions(completeQs);
    } catch (error) {
      console.error("Failed to fetch suggestions", error);
    } finally {
      setLoadingSuggestions(false);
    }
  };

  const handleFileUpload = async (e) => {
    const files = e.target.files;
    if (!files || files.length === 0) return;

    setIsUploading(true);
    setUploadStatus(null);
    setSuggestedQuestions([]);
    setErrorMsg(null);

    try {
      await uploadFiles(files);
      setSystemReady(true);
      setUploadStatus('success');
      // Using concatenation to avoid template literal issues if any
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: "**Analysis Ready!** I have processed " + files.length + " document(s). You can now ask about coverage, exclusions, or valid claims.",
        sources: []
      }]);
      await fetchSuggestedQuestions();
    } catch (error) {
      console.error(error);
      setUploadStatus('error');
      setErrorMsg(error.message);
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: "**Error uploading files:** " + (error.message || "Unknown error"),
        sources: []
      }]);
    } finally {
      setIsUploading(false);
      setFileInputKey(Date.now());
    }
  };

  const handleSend = async (e, overrideInput = null) => {
    if (e) e.preventDefault();
    const textToSend = overrideInput || input;

    if (!textToSend.trim() || isLoading) return;

    const userMessage = textToSend.trim();
    setInput('');
    setMessages(prev => [...prev, { role: 'user', content: userMessage }]);
    setIsLoading(true);
    setErrorMsg(null);

    try {
      const response = await askQuestion(userMessage);
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: response.answer,
        sources: response.sources,
        confidence: response.confidence_score
      }]);
    } catch (error) {
      console.error(error);
      setErrorMsg(error.message);
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: "**Error:** " + (error.message || "Unknown error") + ". Please check your connection or documents.",
        sources: []
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex h-screen bg-slate-50 mesh-bg text-slate-800 font-sans relative overflow-hidden">
      {/* Background Decor */}
      <div className="absolute top-0 left-0 w-full h-2 bg-gradient-to-r from-blue-500 via-indigo-500 to-purple-500 z-50"></div>

      {/* Global Error Toast */}
      {errorMsg && (
        <div className="absolute top-6 left-1/2 transform -translate-x-1/2 z-[60] bg-red-600/90 backdrop-blur-md text-white px-6 py-3 rounded-xl shadow-2xl flex items-center gap-3 animate-in slide-in-from-top-4 border border-red-500/50">
          <AlertCircle className="w-5 h-5 text-white/90" />
          <span className="font-medium tracking-wide">{errorMsg}</span>
          <button onClick={() => setErrorMsg(null)} className="ml-2 opacity-80 hover:opacity-100 hover:bg-white/20 rounded-full p-1 transition-all">✕</button>
        </div>
      )}

      {/* Sidebar */}
      <div className="w-80 glass-panel border-r flex flex-col p-6 hidden md:flex overflow-y-auto relative z-10 transition-all duration-300">
        <h1 className="text-2xl font-extrabold text-transparent bg-clip-text bg-gradient-to-br from-indigo-700 to-purple-600 mb-8 flex items-center gap-3 tracking-tight drop-shadow-sm">
          <span className="bg-blue-100 p-2 rounded-xl border border-blue-200">
            <Files className="w-6 h-6 text-blue-600" />
          </span>
          Policy Analyzer
        </h1>

        <div className="mb-8 group">
          <h2 className="text-xs font-bold text-slate-400 uppercase tracking-widest mb-4 ml-1">Documents</h2>
          <label className={clsx(
            "flex flex-col items-center justify-center w-full h-40 border-2 border-dashed rounded-2xl cursor-pointer transition-all duration-300",
            isUploading
              ? "bg-blue-50 border-blue-400 scale-[0.98]"
              : "border-slate-300 hover:bg-white hover:border-blue-400 hover:shadow-lg hover:shadow-blue-500/10 bg-slate-50/50"
          )}>
            <div className="flex flex-col items-center justify-center pt-5 pb-6">
              {isUploading ? (
                <div className="relative">
                  <div className="absolute inset-0 bg-blue-300 blur-xl opacity-30 animate-pulse rounded-full"></div>
                  <Loader2 className="w-10 h-10 text-indigo-500 animate-spin mb-2 relative z-10 drop-shadow-md" />
                </div>
              ) : (
                <div className="bg-white p-3 rounded-full shadow-sm mb-3 group-hover:scale-110 transition-transform duration-300">
                  <Upload className="w-6 h-6 text-blue-500" />
                </div>
              )}
              <p className="text-sm font-medium text-slate-600 group-hover:text-blue-600 transition-colors">
                {isUploading ? "Analyzing Policy..." : "Upload PDF Policy"}
              </p>
              <p className="text-xs text-slate-400 mt-1">PDF or TXT</p>
            </div>
            <input
              key={fileInputKey}
              type="file"
              className="hidden"
              accept=".pdf,.txt"
              multiple
              onChange={handleFileUpload}
              disabled={isUploading}
            />
          </label>

          {uploadStatus === 'success' && (
            <div className="mt-3 text-emerald-600 text-xs font-medium flex items-center gap-1.5 bg-emerald-50 px-3 py-2 rounded-lg border border-emerald-100 animate-in fade-in slide-in-from-top-1">
              <CheckCircle className="w-3.5 h-3.5" />
              <span>Ready for Analysis</span>
            </div>
          )}
        </div>

        {/* Suggested Questions Section */}
        {(suggestedQuestions.length > 0 || loadingSuggestions) && (
          <div className="mb-8 flex-1 animate-in fade-in duration-500">
            <h2 className="text-xs font-bold text-slate-400 uppercase tracking-widest mb-4 ml-1 flex items-center gap-2">
              <Sparkles className="w-3 h-3 text-amber-500" />
              Risk Discovery
            </h2>

            {loadingSuggestions ? (
              <div className="flex items-center gap-2 text-sm text-slate-400 pl-2">
                <Loader2 className="w-3 h-3 animate-spin" /> Identifying risks...
              </div>
            ) : (
              <div className="flex flex-col gap-2.5">
                {suggestedQuestions.map((q, idx) => (
                  <button
                    key={idx}
                    onClick={() => handleSend(null, q)}
                    disabled={isLoading}
                    className="text-left text-xs sm:text-sm p-3 rounded-xl bg-gradient-to-br from-white to-slate-50 text-slate-700 hover:from-blue-50 hover:to-indigo-50 hover:text-blue-700 transition-all border border-slate-200 hover:border-blue-200 shadow-sm hover:shadow-md flex items-start gap-2.5 group relative overflow-hidden"
                  >
                    <div className="absolute left-0 top-0 w-1 h-full bg-blue-500 scale-y-0 group-hover:scale-y-100 transition-transform origin-top"></div>
                    <HelpCircle className="w-4 h-4 flex-shrink-0 mt-0.5 text-slate-400 group-hover:text-blue-500 transition-colors" />
                    <span className="leading-snug">{q}</span>
                  </button>
                ))}
              </div>
            )}
          </div>
        )}

        <div className="mt-auto pt-4 border-t border-slate-100">
          <div className={clsx(
            "flex items-center gap-3 p-3 rounded-xl border transition-colors",
            systemReady
              ? "bg-emerald-50/50 border-emerald-100"
              : "bg-amber-50/50 border-amber-100"
          )}>
            <div className={clsx("w-2.5 h-2.5 rounded-full shadow-sm animate-pulse", systemReady ? "bg-emerald-500" : "bg-amber-500")} />
            <span className={clsx("text-xs font-bold uppercase tracking-wider", systemReady ? "text-emerald-700" : "text-amber-700")}>
              {systemReady ? "System Active" : "Waiting for Info"}
            </span>
          </div>
        </div>
      </div>

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col max-w-5xl mx-auto w-full h-full relative z-0">
        <header className="p-4 border-b border-white/50 md:hidden flex items-center justify-between glass-panel sticky top-0 z-40">
          <div className="flex items-center gap-2">
            <Files className="w-6 h-6 text-indigo-600" />
            <h1 className="text-lg font-bold text-slate-800">Policy Analyzer</h1>
          </div>
          <div className={clsx("w-2 h-2 rounded-full", systemReady ? "bg-emerald-500" : "bg-amber-500")} />
        </header>

        <div className="flex-1 overflow-y-auto p-4 sm:p-6 space-y-6 scroll-smooth">
          {messages.map((msg, idx) => (
            <div key={idx} className={clsx(
              "flex gap-4 max-w-4xl mx-auto animate-in slide-in-from-bottom-2 duration-500 fill-mode-backwards",
              msg.role === 'user' ? "flex-row-reverse" : "flex-row"
            )} style={{ animationDelay: `${idx * 50}ms` }}>

              <div className={clsx(
                "w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0 shadow-md border-2 border-white",
                msg.role === 'user'
                  ? "bg-gradient-to-br from-blue-600 to-indigo-600 text-white"
                  : "bg-white text-blue-600"
              )}>
                {msg.role === 'user' ? <User className="w-5 h-5" /> : <Bot className="w-6 h-6" />}
              </div>

              <div className={clsx(
                "flex flex-col gap-2 max-w-[85%] sm:max-w-[75%]",
                msg.role === 'user' ? "items-end" : "items-start"
              )}>
                <div className={clsx(
                  "p-5 rounded-3xl text-sm md:text-base leading-relaxed transition-all duration-300",
                  msg.role === 'user'
                    ? "bg-gradient-to-br from-indigo-500 hover:from-indigo-600 to-purple-600 hover:to-purple-700 text-white rounded-br-sm shadow-lg shadow-indigo-500/20 ml-8"
                    : "glass-bubble text-slate-800 rounded-bl-sm mr-8"
                )}>
                  <div className="prose prose-sm max-w-none prose-slate prose-p:my-1 prose-headings:my-2 prose-ul:my-2 prose-li:my-0.5">
                    {typeof msg.content === 'string' ? (
                      <ReactMarkdown
                        remarkPlugins={[remarkGfm]}
                        components={{
                          h1: ({ node, ...props }) => <h1 className="text-lg font-bold text-blue-900 border-b border-blue-100 pb-1 mb-2" {...props} />,
                          h2: ({ node, ...props }) => <h2 className="text-base font-bold text-slate-800 mt-3 mb-1" {...props} />,
                          h3: ({ node, ...props }) => <h3 className="text-sm font-bold text-slate-700 mt-2" {...props} />,
                          ul: ({ node, ...props }) => <ul className="list-disc list-outside ml-4 space-y-1" {...props} />,
                          ol: ({ node, ...props }) => <ol className="list-decimal list-outside ml-4 space-y-1" {...props} />,
                          strong: ({ node, ...props }) => <strong className="font-bold text-slate-900 bg-yellow-50 px-0.5 rounded" {...props} />,
                          blockquote: ({ node, ...props }) => <blockquote className="border-l-4 border-blue-400 pl-3 italic text-slate-500 bg-slate-50 py-1 pr-2 rounded-r" {...props} />,
                        }}
                      >
                        {msg.content}
                      </ReactMarkdown>
                    ) : (
                      <div className="text-red-500 font-mono text-xs p-2 bg-red-50 rounded">Error: Content format invalid</div>
                    )}
                  </div>
                </div>
              </div>
            </div>
          ))}
          {isLoading && (
            <div className="flex gap-4 max-w-4xl mx-auto animate-pulse">
              <div className="w-10 h-10 rounded-full bg-white border-2 border-white shadow-sm flex items-center justify-center">
                <Bot className="w-6 h-6 text-blue-300" />
              </div>
              <div className="p-4 rounded-2xl bg-white w-1/3 min-w-[200px] shadow-sm border border-slate-100 flex items-center gap-3">
                <div className="flex gap-1">
                  <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                  <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                  <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
                </div>
                <span className="text-xs text-slate-400 font-medium">Analyzing Policy...</span>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Input Area */}
        <div className="p-4 md:p-6 glass-panel border-t border-white/60 sticky bottom-0 z-10 transition-all duration-300">
          <form onSubmit={(e) => handleSend(e)} className="max-w-4xl mx-auto relative flex items-center gap-3">
            <div className="relative flex-1 group">
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder={systemReady ? "Ask about exclusions, waiting periods, or limits..." : "Please upload a policy document first..."}
                disabled={!systemReady || isLoading}
                className="w-full p-4 pl-5 pr-14 rounded-2xl border border-slate-300 bg-slate-50 focus:bg-white focus:outline-none focus:ring-4 focus:ring-blue-100 focus:border-blue-500 disabled:bg-slate-100 disabled:text-slate-400 shadow-inner transition-all duration-300 placeholder:text-slate-400"
              />
              <div className="absolute inset-0 rounded-2xl ring-1 ring-inset ring-black/5 pointer-events-none group-focus-within:ring-0"></div>
            </div>

            <button
              type="submit"
              disabled={!input.trim() || isLoading || !systemReady}
              className="absolute right-3 p-2.5 bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-xl hover:shadow-lg hover:shadow-blue-500/30 disabled:from-slate-300 disabled:to-slate-400 disabled:cursor-not-allowed disabled:shadow-none transition-all duration-200 transform active:scale-95"
            >
              {isLoading ? <Loader2 className="w-5 h-5 animate-spin" /> : <Send className="w-5 h-5" />}
            </button>
          </form>
          <div className="text-center mt-3 flex items-center justify-center gap-2 opacity-60 hover:opacity-100 transition-opacity">
            <span className="text-[10px] uppercase tracking-widest text-slate-400 font-bold">Powered by Groq & Llama 3</span>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
