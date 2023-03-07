const interceptResources = ['main_frame', 'sub_frame']

function getDataUri(img) {
  let canvas = document.createElement('canvas')
  canvas.width = img.naturalWidth
  canvas.height = img.naturalHeight
  let ctx = canvas.getContext("2d");
  ctx.drawImage(img, 0, 0, img.naturalWidth, img.naturalHeight, 0, 0, img.naturalWidth, img.naturalHeight);
  return canvas.toDataURL();
}

function convertAllImages() {
  for (let img of document.images) {
    img.setAttribute('src', getDataUri(img))
  }
}

chrome.webRequest.onCompleted.addListener((details) => {

  // only intercept GET requests
  if (details.mothod == 'GET')
    return
  // intercept
  if (!interceptResources.includes(details.type))
    return

  let url = details.url
  chrome.tabs.executeScript(details.tabId,
    { file: "prep_doc.js" },
    (results) => {
      let { title, html } = results[0]
      let params = {
        html: html,
        url: url,
        title: title
      }
      let xhr = new XMLHttpRequest()
      xhr.open("POST", "http://localhost:8888/knowbase", false);
      xhr.setRequestHeader('Content-type', 'application/json')
      xhr.send(JSON.stringify(params))
      let result = xhr.responseText;
      let data = JSON.parse(result)
    }
  )
}, {
  urls: ["*://wiki.bytedance.net/*"]
})


/**
 * 在每个request结束阶段，把相应的request的url还有html发送处来
 * 本地的server接受到这个参数之后，解析其中的内容，把网页存储一份，同时把图片存储一份。
 */