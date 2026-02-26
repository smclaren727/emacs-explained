;;; emacs-explained-ui.el --- UI helpers for Emacs Explained -*- lexical-binding: t; -*-

;;; Commentary:
;; Result buffer helpers for Emacs Explained responses.

;;; Code:

(require 'subr-x)

(defvar emacs-explained-auto-cite-sources)

(defconst emacs-explained-ui-buffer-name "*Emacs Explained*")

;;;###autoload
(define-derived-mode emacs-explained-ui-mode special-mode "Emacs-Explained"
  "Major mode for Emacs Explained responses.")

(defun emacs-explained-ui--insert-sources (sources)
  "Insert SOURCES list into current buffer."
  (when (and emacs-explained-auto-cite-sources sources)
    (insert "Sources\n")
    (insert "-------\n")
    (dolist (source sources)
      (insert (format "- %s\n" source)))
    (insert "\n")))

(defun emacs-explained-ui-show-result (title result)
  "Display RESULT in dedicated buffer with TITLE."
  (let* ((answer (or (alist-get 'answer result) ""))
         (sources (alist-get 'sources result))
         (provider (or (alist-get 'provider result) "unknown"))
         (model (or (alist-get 'model result) "unknown"))
         (buffer (get-buffer-create emacs-explained-ui-buffer-name)))
    (with-current-buffer buffer
      (let ((inhibit-read-only t))
        (erase-buffer)
        (emacs-explained-ui-mode)
        (insert (format "%s\n" title))
        (insert (make-string (length title) ?=))
        (insert "\n\n")
        (insert (format "Provider: %s\nModel: %s\n\n" provider model))
        (insert "Answer\n")
        (insert "------\n")
        (insert (if (string-empty-p answer) "(No answer returned)" answer))
        (insert "\n\n")
        (emacs-explained-ui--insert-sources sources)
        (goto-char (point-min))))
    (pop-to-buffer buffer)))

(provide 'emacs-explained-ui)
;;; emacs-explained-ui.el ends here
