// constants
const UP_EMPTY = '\u25B5\u25B5\u25B5'
const UP_SOLID = '\u25B4\u25B4\u25B4'
const DN_EMPTY = '\u25BF\u25BF\u25BF'
const DN_SOLID = '\u25BE\u25BE\u25BE'
const ROW_LIMIT = 10000;

// states
let shouldScroll = true;

// query all needed elements
const timeP = document.querySelector('#time');
const dateP = document.querySelector('#date');
const buyStreaming = document.querySelector('#buy-streaming');
const sellStreaming = document.querySelector('#sell-streaming');
const buyOrder = document.querySelector('#buy-order');
const sellOrder = document.querySelector('#sell-order');
const topHigh = document.querySelector('#top-high');
const topLow = document.querySelector('#top-low');
const title = document.querySelector('#title');


window.addEventListener("DOMContentLoaded", () => {
    // other initializations
    setInterval(updateTime, 1000);
    title.parentElement.parentElement.addEventListener('click', onTitleClick);
    // websocket and event handlers
    const websocket = new WebSocket(getWebSocketServer());
    websocket.onmessage = onWebsocketMessage;
});


function onTitleClick(event) {
    title.classList.toggle('text-danger');
    shouldScroll = !shouldScroll;
}


function updateTime() {
    const date = new Date();
    timeP.textContent = date.toLocaleTimeString()
    dateP.textContent = date.toLocaleDateString();
}


function onWebsocketMessage({ data }) {
    const { type: name, data: event } = JSON.parse(data);
    switch (name) {
        case "intraday_high":
            populateIntradayHigh(event);
            break;
        case "intraday_low":
            populateIntradayLow(event);
            break;
        case "top_high":
            populateTop(event, 'text-success', topHigh);
            break;
        case "top_low":
            populateTop(event, 'text-danger', topLow);
            break;
        default:
            console.log(`Unsupported event: ${name}, ${event}`);
    }
}


function populateTop(event, color, target) {
    const allDiv = target.querySelectorAll('div');
    for (let i = 0; i < allDiv.length; i++) {
        populateTopSingle(event[i], color, allDiv[i]);
    }
}


function populateTopSingle(item, color, div) {
    const allP = div.querySelectorAll('p');
    if (item === undefined) {
        allP[0].textContent = '';
        allP[1].textContent = '';
        allP[2].textContent = '';
        return
    }
    allP[0].textContent = item['symbol'];
    allP[1].textContent = item['last'];
    allP[2].textContent = `${(Math.round(item['gap'] * 10000) / 100).toFixed(2)}%`;;
}


function populateIntradayHigh(event) {
    populateStreamingRow(event, buyStreaming, 'text-success', UP_EMPTY);
}


function populateIntradayLow(event) {
    populateStreamingRow(event, sellStreaming, 'text-danger', DN_EMPTY);
}


function populateStreamingRow(event, target, color, sign) {
    const [row, lastSymbol] = insertOneRowAtLast(target, 7);
    row.cells[1].textContent = parseDateString(event['time']);
    if (event['symbol'] === lastSymbol) {
        if (sign === UP_EMPTY) {
            sign = UP_SOLID;
        } else if (sign === DN_EMPTY) {
            sign = DN_SOLID;
        } else {
            throw new Error(`Unsupported sign: ${sign}`);
        }
    }
    row.cells[2].textContent = sign;
    row.cells[2].classList.add(color)
    row.cells[3].textContent = event['symbol'];
    row.cells[4].textContent = event['price'];
    row.cells[5].textContent = `${(Math.round(event['gap'] * 10000) / 100).toFixed(2)}%`;
    row.cells[5].classList.add(color)
    row.cells[6].textContent = event['count'];

    if (shouldScroll) {
        // scroll to bottom of the table
        target.parentElement.scrollTo(0, target.parentElement.scrollHeight);
    }
}


function insertOneRowAtLast(target, numCells) {
    // insert a row at the last of the `target` table with `numCells` cells
    // first cell is the index
    const tbody = target.querySelector('tbody');
    const numRow = tbody.rows.length;
    const lastRow = tbody.rows[numRow - 1];
    const lastIdx = lastRow ? parseInt(lastRow.cells[0].textContent) : 0;
    const lastSymbol = lastRow ? lastRow.cells[3].textContent : '';
    const row = tbody.insertRow();
    for (let i = 0; i < numCells; i++) {
        const cell = row.insertCell();
        if (i === 0) {
            cell.textContent = lastIdx + 1;
        }
        cell.className = 'pb-0 pt-1';
    }
    if (numRow >= ROW_LIMIT) {
        tbody.deleteRow(0);
    }
    return [row, lastSymbol];
}

function parseDateString(dateString) {
    // parse date string to time string
    const date = new Date(Date.parse(dateString));
    return date.toLocaleTimeString();
}


function getWebSocketServer() {
    if (window.location.host === "mortimerliu.github.io") {
        return "wss://real-time-trading-a4e8e8f49408.herokuapp.com/";
    } else if (window.location.host === "localhost:8000") {
        return "ws://localhost:5001/";
    } else {
        throw new Error(`Unsupported host: ${window.location.host}`);
    }
}
