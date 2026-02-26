;;; emacs-explained-http.el --- HTTP helpers for Emacs Explained -*- lexical-binding: t; -*-

;;; Commentary:
;; Internal HTTP helpers for Emacs Explained.

;;; Code:

(require 'json)
(require 'url)

(defvar emacs-explained-api-url)
(defvar emacs-explained-http-timeout)

(defun emacs-explained-http--endpoint-url (endpoint)
  "Build full URL for ENDPOINT."
  (concat (replace-regexp-in-string "/\\'" "" emacs-explained-api-url) endpoint))

(defun emacs-explained-http--decode-json-body ()
  "Decode JSON body from current buffer."
  (goto-char (point-min))
  (unless (search-forward "\n\n" nil t)
    (error "Invalid HTTP response from Emacs Explained API"))
  (let ((json-object-type 'alist)
        (json-array-type 'list)
        (json-key-type 'symbol)
        (json-false nil))
    (json-read)))

(defun emacs-explained-http--status-code ()
  "Return HTTP status code from current buffer headers."
  (goto-char (point-min))
  (if (looking-at "HTTP/[0-9.]+ \\([0-9]+\\)")
      (string-to-number (match-string 1))
    0))

(defun emacs-explained-http-post (endpoint payload)
  "POST PAYLOAD JSON to ENDPOINT and return parsed response object."
  (let* ((url-request-method "POST")
         (url-request-extra-headers '(("Content-Type" . "application/json")))
         (url-request-data (encode-coding-string (json-encode payload) 'utf-8))
         (buffer (url-retrieve-synchronously
                  (emacs-explained-http--endpoint-url endpoint)
                  t
                  t
                  emacs-explained-http-timeout)))
    (unless buffer
      (error "No response from Emacs Explained API"))
    (unwind-protect
        (with-current-buffer buffer
          (let ((status (emacs-explained-http--status-code))
                (body (emacs-explained-http--decode-json-body)))
            (when (>= status 400)
              (error "Emacs Explained API error (HTTP %d): %S" status body))
            body))
      (kill-buffer buffer))))

(defun emacs-explained-http-get (endpoint)
  "GET ENDPOINT and return parsed response object."
  (let* ((url-request-method "GET")
         (url-request-extra-headers nil)
         (url-request-data nil)
         (buffer (url-retrieve-synchronously
                  (emacs-explained-http--endpoint-url endpoint)
                  t
                  t
                  emacs-explained-http-timeout)))
    (unless buffer
      (error "No response from Emacs Explained API"))
    (unwind-protect
        (with-current-buffer buffer
          (let ((status (emacs-explained-http--status-code))
                (body (emacs-explained-http--decode-json-body)))
            (when (>= status 400)
              (error "Emacs Explained API error (HTTP %d): %S" status body))
            body))
      (kill-buffer buffer))))

(provide 'emacs-explained-http)
;;; emacs-explained-http.el ends here
