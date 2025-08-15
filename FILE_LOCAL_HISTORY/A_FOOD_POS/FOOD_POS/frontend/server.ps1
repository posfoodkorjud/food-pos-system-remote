# Simple HTTP Server for Frontend
$listener = New-Object System.Net.HttpListener
$listener.Prefixes.Add('http://localhost:5000/')
$listener.Start()

Write-Host "Server running at http://localhost:5000/" -ForegroundColor Green
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow

try {
    while ($listener.IsListening) {
        $context = $listener.GetContext()
        $request = $context.Request
        $response = $context.Response
        
        $localPath = $request.Url.LocalPath
        if ($localPath -eq '/') {
            $localPath = '/order.html'
        }
        
        $filePath = Join-Path $PSScriptRoot $localPath.TrimStart('/')
        
        if (Test-Path $filePath) {
            try {
                $content = Get-Content $filePath -Raw -Encoding UTF8
                $buffer = [System.Text.Encoding]::UTF8.GetBytes($content)
                
                # Set content type based on file extension
                $extension = [System.IO.Path]::GetExtension($filePath).ToLower()
                switch ($extension) {
                    '.html' { $response.ContentType = 'text/html; charset=utf-8' }
                    '.css' { $response.ContentType = 'text/css; charset=utf-8' }
                    '.js' { $response.ContentType = 'application/javascript; charset=utf-8' }
                    '.json' { $response.ContentType = 'application/json; charset=utf-8' }
                    '.png' { $response.ContentType = 'image/png' }
                    '.jpg' { $response.ContentType = 'image/jpeg' }
                    '.jpeg' { $response.ContentType = 'image/jpeg' }
                    '.gif' { $response.ContentType = 'image/gif' }
                    '.svg' { $response.ContentType = 'image/svg+xml' }
                    default { $response.ContentType = 'text/plain' }
                }
                
                $response.ContentLength64 = $buffer.Length
                $response.OutputStream.Write($buffer, 0, $buffer.Length)
                
                Write-Host "$($request.HttpMethod) $($request.Url.LocalPath) - 200 OK" -ForegroundColor Green
            }
            catch {
                $response.StatusCode = 500
                Write-Host "$($request.HttpMethod) $($request.Url.LocalPath) - 500 Internal Server Error" -ForegroundColor Red
            }
        }
        else {
            $response.StatusCode = 404
            $errorContent = "<html><body><h1>404 - File Not Found</h1><p>The requested file was not found.</p></body></html>"
            $buffer = [System.Text.Encoding]::UTF8.GetBytes($errorContent)
            $response.ContentType = 'text/html; charset=utf-8'
            $response.ContentLength64 = $buffer.Length
            $response.OutputStream.Write($buffer, 0, $buffer.Length)
            
            Write-Host "$($request.HttpMethod) $($request.Url.LocalPath) - 404 Not Found" -ForegroundColor Yellow
        }
        
        $response.Close()
    }
}
finally {
    $listener.Stop()
    Write-Host "Server stopped." -ForegroundColor Red
}