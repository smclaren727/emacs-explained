;;; emacs-explained.el --- Emacs client for Emacs Explained API -*- lexical-binding: t; -*-
;; Version: 0.1.0
;; Package-Requires: ((emacs "28.1"))
;; Keywords: tools, help, lisp
;; URL: https://github.com/smclaren727/emacs-explained

;;; Commentary:
;; Client commands for talking to the Emacs Explained backend API.
;; Provides interactive commands for general Q&A and explaining selected elisp.

;;; Code:

(require 'subr-x)
(require 'thingatpt)
(require 'emacs-explained-http)
(require 'emacs-explained-ui)

;;;###autoload
(defgroup emacs-explained nil
  "Emacs client for the Emacs Explained assistant backend."
  :group 'tools
  :prefix "emacs-explained-")

;;;###autoload
(defcustom emacs-explained-api-url "http://127.0.0.1:8000"
  "Base URL for Emacs Explained backend API."
  :type 'string
  :group 'emacs-explained)

;;;###autoload
(defcustom emacs-explained-skill-level "beginner"
  "Default skill level sent to Emacs Explained API."
  :type '(choice (const "beginner") (const "intermediate") (const "advanced"))
  :group 'emacs-explained)

;;;###autoload
(defcustom emacs-explained-auto-cite-sources t
  "When non-nil, display sources in the result buffer."
  :type 'boolean
  :group 'emacs-explained)

;;;###autoload
(defcustom emacs-explained-http-timeout 60
  "HTTP timeout in seconds for API requests."
  :type 'integer
  :group 'emacs-explained)

(defun emacs-explained--read-skill-level ()
  "Prompt for skill level using current default as initial input."
  (completing-read
   "Skill level: "
   '("beginner" "intermediate" "advanced")
   nil
   t
   nil
   nil
   emacs-explained-skill-level))

;;;###autoload
(defun emacs-explained-ask (question skill-level)
  "Ask QUESTION to Emacs Explained at SKILL-LEVEL."
  (interactive
   (list
    (read-string "Ask Emacs Explained: ")
    (emacs-explained--read-skill-level)))
  (unless (string-empty-p question)
    (let ((result (emacs-explained-http-post
                   "/ask"
                   `((question . ,question)
                     (skill_level . ,skill-level)))))
      (emacs-explained-ui-show-result
       (format "Question: %s" question)
       result))))

;;;###autoload
(defun emacs-explained-explain-region (start end skill-level)
  "Explain selected region between START and END using SKILL-LEVEL."
  (interactive
   (if (use-region-p)
       (list (region-beginning) (region-end) (emacs-explained--read-skill-level))
     (user-error "Select a region first")))
  (let* ((code (buffer-substring-no-properties start end))
         (mode (symbol-name major-mode))
         (result (emacs-explained-http-post
                  "/explain-region"
                  `((code . ,code)
                    (language . ,mode)
                    (context . "")
                    (skill_level . ,skill-level)))))
    (emacs-explained-ui-show-result "Explain Region" result)))

;;;###autoload
(defun emacs-explained-explain-defun (skill-level)
  "Explain defun at point using SKILL-LEVEL."
  (interactive (list (emacs-explained--read-skill-level)))
  (let ((bounds (bounds-of-thing-at-point 'defun)))
    (unless bounds
      (user-error "No defun at point"))
    (emacs-explained-explain-region (car bounds) (cdr bounds) skill-level)))

;;;###autoload
(defun emacs-explained-explain-symbol-at-point (skill-level)
  "Explain symbol at point using SKILL-LEVEL."
  (interactive (list (emacs-explained--read-skill-level)))
  (let ((symbol-name (thing-at-point 'symbol t)))
    (unless symbol-name
      (user-error "No symbol at point"))
    (emacs-explained-ask
     (format "Explain what `%s` does in Emacs Lisp and when to use it." symbol-name)
     skill-level)))

(provide 'emacs-explained)
;;; emacs-explained.el ends here
