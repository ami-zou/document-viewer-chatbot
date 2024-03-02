import Modal from "react-modal";
import React, { useState } from "react";
import { Document, Page, pdfjs } from "react-pdf";

const customStyles = {
  content: {
    top: "50%",
    left: "50%",
    right: "auto",
    bottom: "auto",
    marginRight: "-50%",
    transform: "translate(-50%, -50%)",
  },
};

// pdfjs.GlobalWorkerOptions.workerSrc = `https://unpkg.com/pdfjs-dist@${pdfjs.version}/build/pdf.worker.min.js`;

const FileViewer = ({ file, isModalOpen, onClose }) => {
  const handleShare = () => {
    // Implement logic for sharing the file
    console.log("Sharing file:", file.file_name);
  };

  const handleComment = () => {
    // Implement logic for commenting on the file
    console.log("Commenting on file:", file.file_name);
  };

  const handleEdit = () => {
    // Implement logic for editing the file
    console.log("Editing file:", file.file_name);
  };

  return (
    <div>
      <Modal
        isOpen={isModalOpen}
        onRequestClose={onClose}
        style={customStyles}
        contentLabel={file.file_name}
      >
        <div>
          <button onClick={handleShare}>Share</button>
          {file.file_permissions.includes("read") && (
            <button onClick={handleComment}>Comment</button>
          )}
          {file.file_permissions.includes("write") && (
            <button onClick={handleEdit}>Edit</button>
          )}
          <button onClick={onClose}>Close</button>
          <iframe
            src={`data:application/pdf;base64,${file.file_content}`}
            title={file.file_name}
            width="100%"
            height="500px"
          />
        </div>
      </Modal>
    </div>
  );
};

export default FileViewer;
