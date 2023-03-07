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

convertAllImages();

let ret = { title: document.title, html: document.body.innerHTML }

ret
