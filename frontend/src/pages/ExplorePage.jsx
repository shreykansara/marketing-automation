import React, { useState, useEffect } from 'react';
import { 
  Compass, 
  Zap, 
  RefreshCw, 
  ExternalLink, 
  Search,
  Filter,
  CheckCircle2,
  X
} from 'lucide-react';

const ExplorePage = ({ setSystemStatus }) => {
  const [signals, setSignals] = useState([]);
  const [filteredSignals, setFilteredSignals] = useState([]);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [lastStats, setLastStats] = useState(null);
  
  // Filtering states
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedCategory, setSelectedCategory] = useState("all");

  useEffect(() => {
    fetchSignals();
  }, []);

  useEffect(() => {
    applyFilters();
  }, [signals, searchTerm, selectedCategory]);

  const fetchSignals = async () => {
    setLoading(true);
    try {
      const res = await fetch('http://127.0.0.1:8000/api/signals');
      const data = await res.json();
      setSignals(data);
    } catch (err) {
      console.error("Fetch failed", err);
    } finally {
      setLoading(false);
    }
  };

  const applyFilters = () => {
    let result = [...signals];
    
    if (searchTerm) {
      result = result.filter(s => 
        s.title?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        s.content?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        s.company_names?.some(c => c.toLowerCase().includes(searchTerm.toLowerCase()))
      );
    }
    
    if (selectedCategory !== "all") {
      result = result.filter(s => s.category?.toLowerCase() === selectedCategory.toLowerCase());
    }
    
    setFilteredSignals(result);
  };

  const handleGenerate = async () => {
    setGenerating(true);
    setSystemStatus('processing');
    try {
      const res = await fetch('http://127.0.0.1:8000/api/signals/generate', {
        method: 'POST'
      });
      const stats = await res.json();
      setLastStats(stats);
      await fetchSignals();
      setSystemStatus('idle');
    } catch (err) {
      console.error("Generation failed", err);
      setSystemStatus('error');
    } finally {
      setGenerating(false);
    }
  };

  const categories = ["all", ...new Set(signals.map(s => s.category?.toLowerCase()).filter(Boolean))];

  return (
    <div className="page-container">
      <header className="main-header">
        <div>
          <h1 className="header-title outfit">Market Scanner</h1>
          <p className="header-desc">AI-enriched signals curated by relevance</p>
        </div>
        
        <button 
          className="btn btn-primary" 
          onClick={handleGenerate} 
          disabled={generating}
        >
          {generating ? <RefreshCw className="spin" size={20} /> : <Zap size={20} />}
          {generating ? 'Enriching Intelligence...' : 'Scan New Signals'}
        </button>
      </header>

      {lastStats && (
        <div className="stats-alert glass animate-fade-in">
          <CheckCircle2 size={18} color="var(--accent-success)" />
          <span>
            Intelligence scan complete. Successfully curated <strong>{lastStats.enriched_count}</strong> high-intent signals for your registry.
          </span>
          <button className="close-btn" onClick={() => setLastStats(null)}><X size={18} /></button>
        </div>
      )}

      <div className="filter-bar glass">
        <div className="search-box">
          <Search size={18} color="var(--text-muted)" />
          <input 
            type="text" 
            placeholder="Search signals or companies..." 
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>
        
        <div className="filter-tools">
          <div className="category-filter">
            <Filter size={16} />
            <select 
              value={selectedCategory} 
              onChange={(e) => setSelectedCategory(e.target.value)}
              className="category-select"
            >
              {categories.map(cat => (
                <option key={cat} value={cat}>{cat.toUpperCase()}</option>
              ))}
            </select>
          </div>
          <span className="results-count">{filteredSignals.length} signals found</span>
        </div>
      </div>

      <div className="signals-grid">
        {loading ? (
          <div className="empty-state">
            <div className="loader"></div>
            <p>Scanning intelligence database...</p>
          </div>
        ) : filteredSignals.length > 0 ? (
          filteredSignals.map(signal => (
            <SignalCard key={signal._id} signal={signal} />
          ))
        ) : (
          <div className="empty-state glass">
            <Compass size={48} />
            <h3>No Signals Match</h3>
            <p>Try adjusting your search or category filters.</p>
          </div>
        )}
      </div>

      <style jsx>{`
        .spin { animation: spin 1s linear infinite; }
        
        .stats-alert {
          display: flex;
          align-items: center;
          gap: 1.5rem;
          padding: 1.25rem 2rem;
          margin-bottom: 2.5rem;
          background: rgba(16, 185, 129, 0.1);
          border-color: rgba(16, 185, 129, 0.2);
          font-size: 1.05rem;
        }

        .close-btn {
          margin-left: auto;
          background: none;
          border: none;
          color: var(--text-muted);
          cursor: pointer;
          display: flex;
          align-items: center;
        }

        .filter-bar {
          display: flex;
          align-items: center;
          justify-content: space-between;
          padding: 1rem 2rem;
          margin-bottom: 3rem;
          gap: 2rem;
        }

        .search-box {
          display: flex;
          align-items: center;
          gap: 1rem;
          flex: 1;
        }

        .search-box input {
          background: none;
          border: none;
          color: white;
          width: 100%;
          outline: none;
          font-size: 1.1rem;
        }

        .filter-tools {
          display: flex;
          align-items: center;
          gap: 2rem;
        }

        .category-filter {
          display: flex;
          align-items: center;
          gap: 0.75rem;
          background: rgba(255, 255, 255, 0.05);
          padding: 0.5rem 1rem;
          border-radius: 10px;
          border: 1px solid var(--glass-border);
        }

        .category-select {
          background: rgba(15, 18, 50, 0.4);
          border: 1px solid var(--glass-border);
          color: white;
          font-weight: 700;
          font-size: 0.85rem;
          outline: none;
          cursor: pointer;
          padding: 0.4rem 0.75rem;
          border-radius: 8px;
          appearance: none;
        }

        .category-select:focus {
          border-color: var(--accent-primary);
        }

        .category-select option {
          background: var(--bg-deep);
        }

        .results-count {
          font-size: 0.95rem;
          color: var(--text-muted);
          font-weight: 600;
        }

        .signals-grid {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(420px, 1fr));
          gap: 2rem;
        }

        @media (max-width: 640px) {
          .signals-grid { grid-template-columns: 1fr; }
          .filter-bar { flex-direction: column; align-items: stretch; }
        }
      `}</style>
    </div>
  );
};

const SignalCard = ({ signal }) => {
  const getRelevanceClass = (score) => {
    if (score >= 80) return 'high';
    if (score >= 40) return 'medium';
    return 'low';
  };

  return (
    <div className="signal-card glass glass-hover animate-fade-in">
      <div className="card-header">
        <div className={`relevance-badge ${getRelevanceClass(signal.relevance_score)}`}>
          <Zap size={14} />
          {signal.relevance_score}% Relevance
        </div>
        <a href={signal.url} target="_blank" rel="noreferrer" className="btn-icon mini">
          <ExternalLink size={14} />
        </a>
      </div>
      
      <div className="card-body">
        <h3 className="signal-title outfit">{signal.title}</h3>
        <p className="signal-content">{signal.content}</p>
      </div>

      <div className="card-footer">
        <div className="signal-meta">
          <span className="signal-source">{signal.source}</span>
          <span className="dot">•</span>
          <span className="signal-date">
            {new Date(signal.published || signal.created_at).toLocaleDateString()}
          </span>
        </div>
        <div className="company-pill">
          {signal.company_names?.[0] || 'Unknown Origin'}
        </div>
      </div>

      <style jsx>{`
        .signal-card {
          padding: 2rem;
          display: flex;
          flex-direction: column;
          gap: 1.5rem;
        }

        .card-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
        }

        .relevance-badge {
          display: flex;
          align-items: center;
          gap: 0.6rem;
          font-size: 0.85rem;
          font-weight: 800;
          padding: 0.5rem 1rem;
          border-radius: 10px;
          text-transform: uppercase;
        }

        .relevance-badge.high { background: rgba(16, 185, 129, 0.1); color: var(--accent-success); }
        .relevance-badge.medium { background: rgba(245, 158, 11, 0.1); color: var(--accent-warning); }
        .relevance-badge.low { background: rgba(59, 130, 246, 0.1); color: var(--accent-info); }

        .signal-title {
          font-size: 1.35rem;
          line-height: 1.3;
          margin-bottom: 1rem;
          font-weight: 800;
        }

        .signal-content {
          font-size: 1rem;
          color: var(--text-muted);
          line-height: 1.6;
          display: -webkit-box;
          -webkit-line-clamp: 4;
          -webkit-box-orient: vertical;
          overflow: hidden;
        }

        .card-footer {
          margin-top: auto;
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding-top: 1.5rem;
          border-top: 1px solid var(--glass-border);
        }

        .signal-meta {
          display: flex;
          align-items: center;
          gap: 0.75rem;
          font-size: 0.85rem;
          color: var(--text-muted);
          font-weight: 700;
        }

        .company-pill {
          background: var(--glass-shine);
          padding: 0.4rem 0.85rem;
          border-radius: 8px;
          font-size: 0.85rem;
          font-weight: 800;
          color: var(--text-main);
          border: 1px solid var(--glass-border);
        }
      `}</style>
    </div>
  );
};

export default ExplorePage;
