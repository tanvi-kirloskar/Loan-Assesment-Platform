import { useState, useEffect, useCallback } from "react";
import { listDocuments, uploadDocument, ApiError } from "../services/api";

const DOCUMENT_TYPE_OPTIONS = [
  { label: "Payslip", value: "PAYSLIP" },
  { label: "Bank Statement", value: "BANK_STATEMENT" },
  { label: "Tax Return", value: "TAX_RETURN" },
];

function documentTypeLabel(value) {
  const match = DOCUMENT_TYPE_OPTIONS.find((o) => o.value === value);
  return match ? match.label : value;
}

function formatFileSize(bytes) {
  if (!Number.isFinite(bytes)) return "";
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(0)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

export default function DocumentsSection({ applicationId, onSessionExpired }) {
  const [documents, setDocuments] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [listError, setListError] = useState(null);

  const loadDocuments = useCallback(async () => {
    setIsLoading(true);
    setListError(null);

    try {
      const result = await listDocuments(applicationId);
      setDocuments(result);
    } catch (error) {
      if (error instanceof ApiError && error.status === 401) {
        onSessionExpired("Your session has expired. Please log in again.");
        return;
      }

      setListError(
        error instanceof ApiError
          ? error.message
          : "An unexpected error occurred while loading documents."
      );
    } finally {
      setIsLoading(false);
    }
  }, [applicationId, onSessionExpired]);

  useEffect(() => {
    loadDocuments();
  }, [loadDocuments]);

  return (
    <div className="documents-section">
      <h3 className="detail-section-heading">Submitted Documents</h3>
      <p className="documents-intro">
        Documents submitted with this application.
      </p>

      <div className="document-list">
        {isLoading && (
          <p className="dashboard-status-text">Loading documents…</p>
        )}

        {!isLoading && listError && (
          <div className="submit-error" role="alert">
            {listError}
          </div>
        )}

        {!isLoading && !listError && documents.length === 0 && (
          <p className="dashboard-status-text">
            No documents uploaded for this application.
          </p>
        )}

        {!isLoading &&
          !listError &&
          documents.map((doc) => (
            <div className="document-row" key={doc.id}>
              <div>
                <p className="document-row-type">
                  {documentTypeLabel(doc.document_type)}
                  {doc.is_active && (
                    <span className="document-current-tag">Current</span>
                  )}
                </p>
                <p className="document-row-filename">
                  {doc.original_filename}
                  {doc.file_size !== undefined && doc.file_size !== null
                    ? ` · ${formatFileSize(doc.file_size)}`
                    : ""}
                  {doc.version_number
                    ? ` · Version ${doc.version_number}`
                    : ""}
                </p>
              </div>
              <span className="document-status-badge">
                {doc.is_active ? "CURRENT" : "HISTORICAL"}
              </span>
            </div>
          ))}
      </div>
    </div>
  );
}
