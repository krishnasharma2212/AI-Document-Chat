const sidebar = document.getElementById('logo-sidebar');
let isRunning = false


let currentstate = false;

console.log(window.innerWidth)
if (window.innerWidth >= 1328) {
    localStorage.setItem('nav', true);
    currentstate = true
    toggleNav();
};

function toggleNav() {
    let sidebarwidth = window.getComputedStyle(sidebar).width;
    currentstate = !currentstate;
    localStorage.setItem('nav', currentstate);
    if (currentstate) {
        sidebar.style.marginLeft = sidebarwidth;

    } else {
        sidebar.style.marginLeft = "0px";
    }

}


// Function to escape HTML special characters in code blocks
function escapeHtml(html) {
    return html
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#39;');
}


function formatCodeForPrism(rawText) {
    // Match code block with language specified (e.g., ```python ... ```)
    const codeBlockRegex = /```(\w+)([\s\S]*?)```/g;
    let formattedText = rawText;
    let match;

    // Iterate through all code blocks in the text
    while ((match = codeBlockRegex.exec(rawText)) !== null) {
        const language = match[1]; // Extract the language (e.g., python, javascript)
        let code = match[2].trim(); // Extract the code content

        // Escape HTML special characters
        code = code.replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#39;');

        // Create a Prism code block
        const prismCodeBlock = `<pre><code class="language-${language}" data-prismjs-copy="Copy">${code}</code></pre>`;

        // Replace the original code block in the raw text with the formatted one
        formattedText = formattedText.replace(match[0], prismCodeBlock);
    }

    formattedText = convertToHTML(formattedText)

    return formattedText;
}
i = 0
document.addEventListener('keydown', function (event) {
    // Check if Ctrl key and Enter key are pressed
    if (event.ctrlKey && event.key === 'Enter') {
        send();
    }
});

function send(text = null, audio = null) {
    if (isRunning) {
        return
    }
    isRunning = true

    const prompt = document.getElementById('prompt')
    const chats = document.getElementById('chats')

    let UserINP = prompt.value
    if (text) {
        UserINP = text
    }

    prompt.value = "";
    console.log(audio);
    let audioHtml = "";
    if (audio) {
        audioHtml = `<button type="button" onclick="playAudio('${audio}')"
                    class="p-2 inline-flex justify-center items-center gap-x-1 rounded-lg bg-white/10 border border-transparent font-medium text-gray-100 hover:text-gray-600 hover:bg-white focus:outline-none focus:ring-2 ring-offset-blue-600 focus:ring-white focus:ring-offset-2 text-xs">
                    <svg class="shrink-0 size-4" xmlns="http://www.w3.org/2000/svg" width="24"
                        height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor"
                        stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <polygon points="5 3 19 12 5 21 5 3"></polygon>
                    </svg>
                    Voice message
                </button>`

    }

    let fileNames = Object.keys(selectedFiles);
    let FileRaw = `<ul class="flex flex-col justify-end text-start -space-y-px">`

    // Populate the file list
    fileNames.forEach((fileName, index) => {
        FileRaw += `
            <li
                class="flex items-center gap-x-2 p-3 text-sm bg-white border text-gray-800 first:rounded-t-lg first:mt-0 last:rounded-b-lg dark:bg-neutral-900 dark:border-neutral-700 dark:text-neutral-200">
                <div class="w-full flex justify-between truncate">
                    <span class="me-3 flex-1 w-0 truncate">
                        ${fileName} (${(selectedFiles[fileName].size / 1024).toFixed(2)} KB)
                    </span>
                   
                </div>
            </li>`



        // removeBtn.dataset.fileIndex = fileName;


    });
    FileRaw += "</ul>"



    const li = document.createElement('li');

    // Add the classes to the li element
    li.classList.add('max-w-2xl', 'ms-auto', 'flex', 'justify-end', 'gap-x-2', 'sm:gap-x-4');

    const raw = `         <div class="grow text-end space-y-3">
                    <!-- Card -->
                    <div class="inline-block bg-blue-600 rounded-lg p-4 shadow-sm">
                        <p class="text-sm text-white">
                        ${UserINP}
                        </p>
                        ${audioHtml}
                        </div>
                        ${FileRaw}              
                    <!-- End Card -->
                </div>

                <span
                    class="shrink-0 inline-flex items-center justify-center size-[38px] rounded-full bg-gray-600">
                    <span class="text-sm font-medium text-white leading-none">UK</span>
                </span>`

    li.innerHTML = raw;

    chats.appendChild(li);

    scrollToBottom();
    const liAI = document.createElement('li');

    // Add the classes to the li element
    liAI.classList.add('flex', 'gap-x-2', 'sm:gap-x-4');
    i += 1
    const rawAI = `
<img src="/static/logo.jpg" class="rounded-full" alt="" style="
width: 38px;
height: 38px;
">

<div class="grow max-w-[90%] md:max-w-2xl w-full space-y-3">
<!-- Card -->
<div class="bg-white border border-gray-200 rounded-lg p-4 space-y-3 dark:bg-neutral-900 dark:border-neutral-700">
    <span class="text-gray-800 dark:text-white" style="white-space: pre-wrap;" id="AI-${i}"></span>
    <code style="display:none;white-space: pre-wrap;" id="AI-copy-${i}" ></code>
</div>
<!-- End Card -->



<div>
    <div class="sm:flex sm:justify-between">
        <div>
            
            <button type="button" class="py-2 px-3 inline-flex items-center gap-x-2 text-sm rounded-full border border-transparent text-gray-500 hover:bg-gray-50 focus:outline-none focus:bg-gray-50 disabled:opacity-50 disabled:pointer-events-none dark:text-neutral-400 dark:hover:bg-neutral-800 dark:focus:bg-neutral-800" onclick="copy('AI-copy-${i}')">
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-copy" viewBox="0 0 16 16">
<path fill-rule="evenodd" d="M4 2a2 2 0 0 1 2-2h8a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2zm2-1a1 1 0 0 0-1 1v8a1 1 0 0 0 1 1h8a1 1 0 0 0 1-1V2a1 1 0 0 0-1-1zM2 5a1 1 0 0 0-1 1v8a1 1 0 0 0 1 1h8a1 1 0 0 0 1-1v-1h1v1a2 2 0 0 1-2 2H2a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h1v1z"></path>
</svg>
                Copy
            </button>
            
        </div>

        <div class="mt-1 sm:mt-0">
            <button type="button" class="py-2 px-3 inline-flex items-center gap-x-2 text-sm rounded-full border border-transparent text-gray-500 hover:bg-gray-50 focus:outline-none focus:bg-gray-50 disabled:opacity-50 disabled:pointer-events-none dark:text-neutral-400 dark:hover:bg-neutral-800 dark:focus:bg-neutral-800" onclick="send('${UserINP}')">
                <svg class="size-3.5" xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
                    <path fill-rule="evenodd" d="M8 3a5 5 0 1 0 4.546 2.914.5.5 0 0 1 .908-.417A6 6 0 1 1 8 2v1z">
                    </path>
                    <path d="M8 4.466V.534a.25.25 0 0 1 .41-.192l2.36 1.966c.12.1.12.284 0 .384L8.41 4.658A.25.25 0 0 1 8 4.466z">
                    </path>
                </svg>
                New answer
            </button>
        </div>
    </div>
</div>

`
    liAI.innerHTML = rawAI
    chats.append(liAI)
    sendPrompt(UserINP, document.getElementById(`AI-${i}`))
    document.getElementById('stop').style.display = "flex"



}
function copy(ele) {
    const text = document.getElementById(ele).innerText; // Get the text from the input field
    navigator.clipboard.writeText(text)
        .then(() => {
            showToast()
        })
        .catch(err => {
            showToast('Failed to copy text: ', err);
        });
}
let NewResponse = ""
function displayResponse(response, element) {
    scrollToBottom();
    if (!isRunning) {
        return
    }
    if (!response) {
        document.getElementById('stop').style.display = "none"

        NewResponse = ""
        isRunning = false
        return
    }
    document.getElementById(`AI-copy-${i}`).innerHTML += response


    NewResponse += response

    element.innerHTML = formatCodeForPrism(NewResponse);

    scrollToBottom();
    Prism.highlightAll();


}
function convertToHTML(text) {
    // Convert headings (e.g., # Heading, ## Heading)
    text = text.replace(/^(#{1,6})\s*(.*?)$/gm, (match, p1, p2) => {
        const level = p1.length;
        return `<h${level}>${p2}</h${level}>`;
    });

    // Convert bold text (e.g., **bold**)
    text = text.replace(/\*\*(.*?)\*\*/g, '<b>$1</b>');

    // Convert italic text (e.g., _italic_)
    text = text.replace(/_(.*?)_/g, '<i>$1</i>');

    // Convert strikethrough text (e.g., ~~strike~~)
    text = text.replace(/~~(.*?)~~/g, '<del>$1</del>');

    // Convert inline code (e.g., `code`)
    text = text.replace(/`(.*?)`/g, '<code>$1</code>');

    // Convert unordered lists (e.g., - item)
    text = text.replace(/^- (.*)$/gm, '<ul><li>$1</li></ul>');

    // Merge multiple consecutive <ul> tags into one list
    text = text.replace(/<\/ul>\n<ul>/g, '');

    // Convert ordered lists (e.g., 1. item)
    text = text.replace(/^\d+\. (.*)$/gm, '<ol><li>$1</li></ol>');

    // Merge multiple consecutive <ol> tags into one list
    text = text.replace(/<\/ol>\n<ol>/g, '');

    // Return the final HTML
    return text;
}

function scrollToBottom() {
    const chatBox = document.getElementById('chatBox');
    if (chatBox) {
        chatBox.scrollTop = chatBox.scrollHeight; // Scroll to the bottom
    }
}


async function sendPrompt(prompt, element) {



    try {
        const formData = new FormData();

        // Append all selected files to the FormData object
        for (let fileName in selectedFiles) {
            formData.append('files', selectedFiles[fileName]);
        }
        selectedFiles = {}
        RecordingFile = undefined;
        updateFileList()

        // Append additional text data to the FormData object
        formData.append('prompt', prompt);
        const url = new URL(window.location.href);

        // 2. Create a URLSearchParams object from the query string
        const params = new URLSearchParams(url.search);

        // 3. Extract individual parameters
        let chatId = params.get('chat');
        formData.append('chatId', chatId);

        const response = await fetch('/generate', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {

            return;
        }
        // Retrieve Chat-Id from the response headers
        chatId = response.headers.get('Chat-Id');

        // Create a URLSearchParams object from the current query string
        let params2 = new URLSearchParams(url.search);

        // Add or update query parameters
        params2.set('chat', chatId);

        // Set the modified query parameters back to the URL
        url.search = params2.toString();
        window.history.pushState({}, '', url);

        // Alternatively, use history.replaceState to replace the current history entry
        // window.history.replaceState({}, '', url);

        // Read the response stream
        const reader = response.body.getReader();
        const decoder = new TextDecoder('utf-8');




        while (true) {
            const { done, value } = await reader.read();
            if (done) break;
            const chunk = decoder.decode(value, { stream: true });


            displayResponse(chunk, element);
        }

        displayResponse(false, element)

    } catch (error) {
        console.error('Error:', error);
        displayResponse('Error occurred while fetching the response.')
    }
}
function showToast(text = null) {
    const toast = document.getElementById('toast');
    if (text) {
        toast.innerText = text; // Update the toast text if provided
    }

    // Add the animation class to show the toast
    toast.classList.add('toast-show');

    // Set opacity and pointer-events to make it visible
    toast.style.opacity = '1';
    toast.style.pointerEvents = 'auto';

    // Hide the toast after 3 seconds
    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.pointerEvents = 'none';
        toast.classList.remove('toast-show');
    }, 3000); // Duration before hiding
}




const fileInput = document.getElementById('fileInput');

// Object to store selected files
let selectedFiles = {};
let RecordingFile;
// Function to update the file count and list
function updateFileList() {
    const uploadList = document.getElementById("upload")
    uploadList.innerHTML = ""

    if (RecordingFile) {
        button = document.createElement('button')
        button.classList.add(
            "inline-flex", "justify-center", "items-center", "gap-x-1", "rounded-lg",
            "font-medium", "text-gray-800", "hover:text-blue-600", "focus:outline-none",
            "focus:text-blue-600", "text-xs", "sm:text-sm", "dark:text-neutral-200",
            "dark:hover:text-blue-500", "dark:focus:text-blue-500"
        );
        button.innerHTML = `<svg class="shrink-0 size-4" xmlns="http://www.w3.org/2000/svg" width="24" height="24"
                                    fill="currentColor" class="bi bi-file-earmark-fill" viewBox="0 0 16 16">
                                    <path
                                        d="M4 0h5.293A1 1 0 0 1 10 .293L13.707 4a1 1 0 0 1 .293.707V14a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V2a2 2 0 0 1 2-2m5.5 1.5v2a1 1 0 0 0 1 1h2z" />
                                        </svg>
                                        <span style="width: 150px;" class="truncate">${RecordingFile.name} (${(RecordingFile.size / 1024).toFixed(2)} KB)</span>`

        uploadList.appendChild(button)
    }

    let fileNames = Object.keys(selectedFiles);


    // Populate the file list
    fileNames.forEach((fileName, index) => {


        button = document.createElement('button')
        button.classList.add(
            "inline-flex", "justify-center", "items-center", "gap-x-1", "rounded-lg",
            "font-medium", "text-gray-800", "hover:text-blue-600", "focus:outline-none",
            "focus:text-blue-600", "text-xs", "sm:text-sm", "dark:text-neutral-200",
            "dark:hover:text-blue-500", "dark:focus:text-blue-500"
        );
        button.innerHTML = `<svg class="shrink-0 size-4" xmlns="http://www.w3.org/2000/svg" width="24" height="24"
                                    fill="currentColor" class="bi bi-file-earmark-fill" viewBox="0 0 16 16">
                                    <path
                                        d="M4 0h5.293A1 1 0 0 1 10 .293L13.707 4a1 1 0 0 1 .293.707V14a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V2a2 2 0 0 1 2-2m5.5 1.5v2a1 1 0 0 0 1 1h2z" />
                                        </svg>
                                        <span style="width: 150px;" class="truncate">${fileName} (${(selectedFiles[fileName].size / 1024).toFixed(2)} KB)</span>`

        uploadList.appendChild(button)

        // removeBtn.dataset.fileIndex = fileName;


    });
}

// Function to handle file selection
fileInput.addEventListener('change', function (event) {
    // Add files to selectedFiles object
    Array.from(event.target.files).forEach(file => {
        selectedFiles[file.name] = file;
    });

    updateFileList();
});





let mediaRecorder;
let audioChunks = [];

// Function to start recording audio
async function startRecording() {
    try {
        // Request permission and access to the microphone
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });

        // Initialize the MediaRecorder with the stream
        mediaRecorder = new MediaRecorder(stream);

        // Clear previous audio chunks
        audioChunks = [];

        // When data is available, push it to audioChunks
        mediaRecorder.ondataavailable = event => {
            audioChunks.push(event.data);
        };

        // Start recording
        mediaRecorder.start();
        document.getElementById('mic').setAttribute('onclick', 'stopRecording()')
        document.getElementById('stopMic').style.display = "block"
        document.getElementById('play').style.display = "none"
    } catch (error) {
        console.error('Error accessing microphone:', error);
    }
}


function playAudio(url) {
    const audioPlayer = document.getElementById('player')
    audioPlayer.src = url;
    audioPlayer.play()
}
// Function to stop recording audio
function stopRecording() {
    if (mediaRecorder && mediaRecorder.state !== 'inactive') {
        // Stop the MediaRecorder
        mediaRecorder.stop();

        // Convert the audio chunks to a Blob and create a file from it
        mediaRecorder.onstop = () => {
            const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
            const audioFile = new File([audioBlob], 'recording.wav', { type: 'audio/wav' });




            selectedFiles[audioFile.name] = audioFile;

            document.getElementById('mic').setAttribute('onclick', 'startRecording()')
            document.getElementById('stopMic').style.display = "none"
            document.getElementById('play').style.display = "block"

            console.log(audioBlob)
            // Create a URL for the Blob and set it as the source of the audio element
            const audioURL = URL.createObjectURL(audioBlob).toString();
            console.log(audioURL)

            send(null, audioURL);


            if (RecordingFile) {
                size = `${(RecordingFile.size / 1024).toFixed(2)} KB`
                console.log(size)


            }

        };
    }
}