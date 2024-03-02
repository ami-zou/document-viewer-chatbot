import React, { useState, useEffect } from "react";
import Modal from "react-modal";
import FileViewer from "./FileViewer";

const FileExplorer = ({ files }) => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [isModalOpen, setIsModalOpen] = useState(false);

  useEffect(() => {
    Modal.setAppElement("#root");
  }, []);

  //   if (!isModalOpen) {
  //     Modal.setAppElement("#root");
  //   }

  const handleFileClick = (file) => {
    setSelectedFile(file);
    setIsModalOpen(true);
  };

  const closeModal = () => {
    console.log("Closing File Viewer for: ", selectedFile.file_name);
    setSelectedFile(null);
    setIsModalOpen(false);
  };

  return (
    <div>
      {files.map((file) => (
        // <div key={file.file_name} onClick={() => onFileClick(file)}>
        <div key={file.file_name} onClick={() => handleFileClick(file)}>
          <p>{file.file_type === "folder" ? "📁" : "📄"}</p>
          <p>{file.file_name}</p>
        </div>
      ))}

      {selectedFile && (
        <FileViewer
          file={selectedFile}
          isModalOpen={isModalOpen}
          onClose={closeModal}
        />
      )}
    </div>
  );
};

export default FileExplorer;
