import { useState, useEffect } from "react";
import { IP } from "./config";

const FileConversionProgress = ({ conversionId, onComplete }) => {
    const [progress, setProgress] = useState(0);
    const [downloadUrl, setDownloadUrl] = useState(null);
    const [status, setStatus] = useState("Waiting to start...");
    const [lastProgressChangeAt, setLastProgressChangeAt] = useState(Date.now());
    const [startedAt, setStartedAt] = useState(null);
    const [elapsedSeconds, setElapsedSeconds] = useState(0);
    const [isDownloading, setIsDownloading] = useState(false);

    useEffect(() => {
        if (!conversionId) return;  // Prevent running if conversionId is null

        setStartedAt(Date.now());
        setElapsedSeconds(0);
        setLastProgressChangeAt(Date.now());
        setStatus("Queued...");

        const interval = setInterval(() => {
            fetch(`${IP}/progress/${conversionId}`, { // fetch the route from from the backend, DO NOT set 'Content-Type': 'application/json' for FormData
                method: 'GET',
                mode: "cors",
                credentials: "include"
            })
                .then(res => res.json())
                .then(data => {
                    setProgress((prev) => {
                        if (typeof data.progress === "number" && data.progress > prev) {
                            setLastProgressChangeAt(Date.now());
                        }
                        return data.progress ?? prev;
                    });
                    if (data.status) {
                        setStatus(data.status);
                    }
                    console.log("Progress:", data.progress);

                    if (data.progress >= 100) {
                        setDownloadUrl(`${IP}/download/${conversionId}`);  // Set the file URL
                        // console.log("Download URL:", downloadUrl);
                        clearInterval(interval);  // Stop polling when done
                        // onComplete();
                    }
                })
                .catch(err => console.error("Error fetching progress:", err));
        }, 1000);

        return () => clearInterval(interval);  // Cleanup on unmount
    }, [conversionId]);

    useEffect(() => {
        if (!startedAt || progress >= 100) return;

        const timer = setInterval(() => {
            setElapsedSeconds(Math.floor((Date.now() - startedAt) / 1000));
        }, 1000);

        return () => clearInterval(timer);
    }, [startedAt, progress]);

    const stalledForSeconds = Math.floor((Date.now() - lastProgressChangeAt) / 1000);
    const isStalled = progress > 0 && progress < 100 && stalledForSeconds >= 12;
    const elapsedDisplay = `${Math.floor(elapsedSeconds / 60)}m ${elapsedSeconds % 60}s`;

    const handleDownload = async () => {
        if (!downloadUrl || !conversionId || isDownloading) {
            return;
        }

        setIsDownloading(true);

        try {
            const response = await fetch(downloadUrl, {
                method: "GET",
                mode: "cors",
                credentials: "include",
            });

            if (!response.ok) {
                throw new Error("Download failed");
            }

            const blob = await response.blob();
            const objectUrl = window.URL.createObjectURL(blob);
            const link = document.createElement("a");
            const disposition = response.headers.get("content-disposition");
            const matchedFilename = disposition?.match(/filename\*?=(?:UTF-8''|\")?([^";]+)/i);
            const filename = matchedFilename ? decodeURIComponent(matchedFilename[1].replace(/\"/g, "")) : "converted-file";

            link.href = objectUrl;
            link.download = filename;
            document.body.appendChild(link);
            link.click();
            link.remove();
            window.URL.revokeObjectURL(objectUrl);

            await fetch(`${IP}/cleanup/${conversionId}`, {
                method: "POST",
                mode: "cors",
                credentials: "include",
            });

            if (onComplete) {
                onComplete();
            } else {
                window.location.reload();
            }
        } catch (error) {
            console.error("Error downloading file:", error);
            setStatus("Download failed. Please try again.");
        } finally {
            setIsDownloading(false);
        }
    };

    return (
        <div className="card card-border bg-base-100 w-96 mt-5">
            <div className="card-body">
                <h2 className="card-title">Progress</h2>
                <progress className="progress progress-accent w-56" value={progress} max="100"></progress>
                <p>{progress}%</p>
                <p className="text-sm opacity-80">{status}</p>
                <p className="text-xs opacity-70">Elapsed: {elapsedDisplay}</p>
                {isStalled && (
                    <div className="alert alert-info py-2 mt-2">
                        <span className="text-sm">Still converting in the background. Large files can stay at one percentage for a while.</span>
                    </div>
                )}
                
                <div className="card-actions justify-end">
                    {downloadUrl ? (
                        <button className="btn btn-primary" onClick={handleDownload} disabled={isDownloading}>
                            Download
                        </button>
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
