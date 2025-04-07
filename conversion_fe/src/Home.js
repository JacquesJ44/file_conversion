import { useState, useEffect } from "react";
import { IP } from "./config";
import FileConversionProgress from "./FileConversionProgress";

const Home = () => {

    // Forms fields
    const [conversion, setConversion] = useState('');
    const [toFormat, setToFormat] = useState('');
    const [file, setFile] = useState('');
    const [conversionId, setConversionId] = useState(null);  // Store the conversion ID

    // Setting Conversions and Conversion Types variables for selection in cascading style, followed by functions to set in the form defined above 
    const conversions = [
        {
            conversion: 'Audio',
            type: ['mp3', 'wav', 'ogg', 'flac']
               
        },
        {
            conversion: 'Video',
            type: ['mp4', 'avi', 'mov', 'mkv', 'webm']
        },
        {
            conversion: 'Images',
            type: ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp', 'svg']
            
        },
        {
            conversion: 'Archives',
            type: ['zip', 'rar', '7z', 'tar.gz']
            
        },
        {
            conversion: 'Documents',
            type: ['docx', 'pdf', 'txt', 'odt']
            
        }
    ]

    const [toFormats, setToFormats] = useState([])

    const changeConversion = (e) => {
        setConversion(e.target.value);
        setToFormats(conversions.find((v) => v.conversion === e.target.value).type);
    }
    
    const changeToFormat = (e) => {
        setToFormat(e.target.value);
    }

    useEffect(() => {
        fetch(`${IP}/`, {
          method: "GET",
          mode: "cors",
          credentials: "include", // if you're using cookies
        }).catch((err) => console.error("Cleanup GET failed:", err));
      }, []);

    // 1. Upload the data and the file 
    const handleSubmit = (e) => {
        e.preventDefault()
        // Create a FormData instance to append information and files
        const formData = new FormData();
            formData.append('conversion', conversion);
            formData.append('toFormat', toFormat);
            formData.append('formFile', file);
        
        fetch(`${IP}/convert`, { // fetch the route from from the backend, DO NOT set 'Content-Type': 'application/json' for FormData
            method: 'POST',
            body: formData, //send formData
            mode: "cors",
            credentials: "include"
        })
        .then((res) => res.json()) // Convert the response to JSON
        .then(data => {
            console.log(data)
            if (data.error) {
                alert(data.error)
            } else if (data.conversion_id) {
                setConversionId(data.conversion_id);  // Set conversion ID to track progress
            }
        })
        .catch((err) => console.error('Upload failed:', err));
    }

    // Reset the form after conversion is complete
    const handleConversionComplete = () => {
        window.location.reload();
        // setConversionId(null);
        // setConversion('');
        // // changeConversion = (e);
        // setToFormat('');
        // setFile('');
        // setToFormats([]);
    };

    return (  
        <div className="card-body">
            <form onSubmit={handleSubmit}>
                <div className="flex items-justify mt-5">
                    <div className="form-control mx-1">
                        <label className="label">
                            <span className="label-text">Convert</span>    
                        </label>
                        <select onChange={changeConversion} id="conversion" className="input input-bordered w-full max-w-xs" defaultValue='' required>
                            <option value=''>Choose an option...</option>
                                {conversions.map((v, index) => {
                                    return (
                                        <option key={index} value={v.conversion}>{v.conversion}</option>
                                    )
                                })}
                        </select>
                    </div>

                    <div className="form-control mx-1">
                        <label className="label">
                            <span className="label-text">To Format</span>    
                        </label>
                        <select onChange={changeToFormat} id="toFormat" className="input input-bordered w-full max-w-xs" defaultValue='' required>
                            <option value=''>Choose an option...</option>
                                {toFormats.map((c, index) => {
                                        return (
                                            <option key={index} value={c}>{c}</option>
                                        )
                                    })}
                        </select>
                    </div>

                    <div className="form-control mx-1">
                        <label className="label">
                            <span className="label-text">Upload File</span>    
                        </label>
                        <input
                            className="relative m-0 block w-full min-w-0 flex-auto rounded border border-solid border-neutral-300 bg-clip-padding px-3 py-[0.32rem] text-base font-normal text-neutral-700 transition duration-300 ease-in-out file:-mx-3 file:-my-[0.32rem] file:overflow-hidden file:rounded-none file:border-0 file:border-solid file:border-inherit file:bg-neutral-100 file:px-3 file:py-[0.32rem] file:text-neutral-700 file:transition file:duration-150 file:ease-in-out file:[border-inline-end-width:1px] file:[margin-inline-end:0.75rem] hover:file:bg-neutral-200 focus:border-primary focus:text-neutral-700 focus:shadow-te-primary focus:outline-none dark:border-neutral-600 dark:text-neutral-200 dark:file:bg-neutral-700 dark:file:text-neutral-100 dark:focus:border-primary"
                            required
                            type="file"
                            id="formFile"
                            onChange={(e) => setFile(e.target.files[0])}
                            />
                    </div>
                </div>
                <div className="form-control mt-9 ml-1">
                    <button className="btn btn-accent w-full max-w-xs">Convert</button>
                </div>
            </form>
            {/* <p>Conversion: {conversion}</p>
            <p>toFormat: {toFormat}</p>
            <p>File: {file.name}</p> */}
            {<FileConversionProgress conversionId={conversionId} onComplete={handleConversionComplete} />}
        </div>
    );
}
 
export default Home;
