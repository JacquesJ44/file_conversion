import { useState, useEffect } from "react";
import { IP } from "./config";

const FileConversionProgress = ({ conversionId, onComplete }) => {
    const [progress, setProgress] = useState(0);
    const [downloadUrl, setDownloadUrl] = useState(null);

    useEffect(() => {
        if (!conversionId) return;  // Prevent running if conversionId is null

        const interval = setInterval(() => {
            fetch(`${IP}/progress/${conversionId}`, { // fetch the route from from the backend, DO NOT set 'Content-Type': 'application/json' for FormData
                method: 'GET',
                mode: "cors",
                credentials: "include"
            })
                .then(res => res.json())
                .then(data => {
                    setProgress(data.progress);  // Update progress
                    console.log("Progress:", data.progress);

                    if (data.progress >= 100) {
                        setDownloadUrl(`${IP}/download/${conversionId}`);  // Set the file URL
                        // console.log("Download URL:", downloadUrl);
                        clearInterval(interval);  // Stop polling when done
                        // onComplete();
                    }
                })
                .catch(err => console.error("Error fetching progress:", err));
        }, 1000);  // Poll every 2 seconds

        return () => clearInterval(interval);  // Cleanup on unmount
    }, [conversionId]);

    return (
        <div className="card card-border bg-base-100 w-96 mt-5">
            <div className="card-body">
                <h2 className="card-title">Progress</h2>
                <progress className="progress progress-accent w-56" value={progress} max="100"></progress>
                <p>{progress}%</p>
                
                <div className="card-actions justify-end">
                    {downloadUrl ? (
                        <a href={downloadUrl} className="btn btn-primary" download 
                        onClick={() => {
                            // Refresh the window after the download starts
                            setTimeout(() => {
                                window.location.reload(); // Refresh the page after a short delay
                            }, 500); // Small delay to ensure download starts
                        }}
                        >
                            Download
                        </a>
                    ) : (
                        <button className="btn btn-disabled">Download</button>
                    )}
                </div>
            </div>
            {/* <p>{`Conversion ID: ${conversionId}`}</p>
            <p>{`Download URL: ${downloadUrl}`}</p> */}
        </div>
    );
};

export default FileConversionProgress;
