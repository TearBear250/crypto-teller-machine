const { contextBridge, ipcRenderer } = require('electron')
contextBridge.exposeInMainWorld('electronAPI', {
  printPage: () => ipcRenderer.invoke('print-page'),
})
