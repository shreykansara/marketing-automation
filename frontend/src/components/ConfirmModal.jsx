import React from 'react';
import { AlertTriangle, X } from 'lucide-react';

const ConfirmModal = ({ isOpen, onClose, onConfirm, title, message, confirmText = "Confirm Delete", type = "danger" }) => {
  if (!isOpen) return null;

  return (
    <div className="modal-overlay animate-fade-in" onClick={onClose}>
      <div className="modal-container glass animate-slide-up" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <div className={`modal-icon-bg ${type}`}>
            <AlertTriangle size={20} />
          </div>
          <h3 className="outfit">{title}</h3>
          <button className="close-btn" onClick={onClose}>
            <X size={18} />
          </button>
        </div>

        <div className="modal-body">
          <p>{message}</p>
        </div>

        <div className="modal-footer">
          <button className="btn btn-outline" onClick={onClose}>
            Cancel
          </button>
          <button className={`btn ${type === 'danger' ? 'btn-danger' : 'btn-primary'}`} onClick={onConfirm}>
            {confirmText}
          </button>
        </div>
      </div>

      <style jsx>{`
        .modal-overlay {
          position: fixed;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          background: rgba(0, 0, 0, 0.7);
          backdrop-filter: blur(4px);
          display: flex;
          align-items: center;
          justify-content: center;
          z-index: 1000;
          padding: 1.5rem;
        }

        .modal-container {
          width: 100%;
          max-width: 450px;
          padding: 1.5rem;
          background: rgba(15, 18, 30, 0.9);
          border: 1px solid var(--glass-border);
          box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
        }

        .modal-header {
          display: flex;
          align-items: center;
          gap: 1rem;
          margin-bottom: 1rem;
        }

        .modal-icon-bg {
          width: 40px;
          height: 40px;
          border-radius: 10px;
          display: flex;
          align-items: center;
          justify-content: center;
        }

        .modal-icon-bg.danger {
          background: rgba(239, 68, 68, 0.2);
          color: var(--accent-danger);
        }

        .modal-header h3 {
          flex: 1;
          font-size: 1.25rem;
          margin: 0;
        }

        .close-btn {
          background: none;
          border: none;
          color: var(--text-muted);
          cursor: pointer;
          padding: 5px;
          transition: 0.2s;
        }

        .close-btn:hover { color: white; }

        .modal-body {
          margin-bottom: 2rem;
          color: var(--text-muted);
          line-height: 1.6;
          font-size: 0.95rem;
        }

        .modal-footer {
          display: flex;
          justify-content: flex-end;
          gap: 1rem;
        }

        .btn-danger {
          background: var(--accent-danger);
          color: white;
          box-shadow: 0 4px 12px rgba(239, 68, 68, 0.3);
        }

        .btn-danger:hover {
          background: #dc2626;
        }

        @keyframes fadeIn {
          from { opacity: 0; }
          to { opacity: 1; }
        }

        @keyframes slideUp {
          from { transform: translateY(20px); opacity: 0; }
          to { transform: translateY(0); opacity: 1; }
        }

        .animate-fade-in { animation: fadeIn 0.3s ease; }
        .animate-slide-up { animation: slideUp 0.3s cubic-bezier(0.16, 1, 0.3, 1); }
      `}</style>
    </div>
  );
};

export default ConfirmModal;
