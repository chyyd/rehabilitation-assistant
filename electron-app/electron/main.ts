/**
 * Electron主进程
 */
import { app, BrowserWindow, ipcMain } from 'electron'
import path from 'path'

let mainWindow: BrowserWindow | null = null

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1400,
    height: 900,
    minWidth: 1200,
    minHeight: 700,
    frame: true,
    titleBarStyle: 'default',
    backgroundColor: '#F2F2F7',
    webPreferences: {
      // 开发环境：Vite编译后的preload在dist-electron/index.js
      // 生产环境：preload与main.js在同一目录
      preload: path.join(__dirname, 'index.js'),
      nodeIntegration: false,
      contextIsolation: true,
      webSecurity: true
    }
  })

  // 开发环境加载Vite开发服务器
  if (process.env.VITE_DEV_SERVER_URL) {
    mainWindow.loadURL(process.env.VITE_DEV_SERVER_URL)
    // mainWindow.webContents.openDevTools() // 已禁用开发者工具
  } else {
    // 生产环境加载打包后的文件
    mainWindow.loadFile(path.join(__dirname, '../dist/index.html'))
  }

  mainWindow.on('closed', () => {
    mainWindow = null
  })
}

// API代理 - 与Python后端通信
ipcMain.handle('api-request', async (event, options) => {
  const { method, url, data } = options

  try {
    const response = await fetch(`http://127.0.0.1:8000${url}`, {
      method,
      headers: {
        'Content-Type': 'application/json'
      },
      body: data ? JSON.stringify(data) : undefined
    })

    // 处理非JSON响应
    const contentType = response.headers.get('content-type')
    let result: any

    if (contentType && contentType.includes('application/json')) {
      result = await response.json()
    } else {
      result = await response.text()
    }

    if (!response.ok) {
      return {
        success: false,
        error: result.detail || result,
        status: response.status
      }
    }

    return { success: true, data: result }
  } catch (error: any) {
    console.error('API请求失败:', error)
    return {
      success: false,
      error: error.message || '网络请求失败'
    }
  }
})

// 健康检查 - 检查后端是否运行
ipcMain.handle('health-check', async () => {
  try {
    const response = await fetch('http://127.0.0.1:8000/health')
    const data = await response.json()
    return { success: true, data }
  } catch (error: any) {
    return {
      success: false,
      error: '后端服务未启动，请先运行 python main.py'
    }
  }
})

app.on('ready', createWindow)

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit()
  }
})

app.on('activate', () => {
  if (mainWindow === null) {
    createWindow()
  }
})
