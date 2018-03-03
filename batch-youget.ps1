Copy-Item vlist.txt vlist-old.txt

foreach($line in Get-Content -Encoding UTF8 .\vlist.txt) {
    if ($line -match "https.*") {
        Write-Output $line
        if (!(Test-Path -Path Downloaded)) {
            New-Item -ItemType directory -Path Downloaded
        }
        while ($counter -ne 5) {
            Try{
                $json = you-get.exe --json --format=mp4 $line | ConvertFrom-Json
                if ([int]($json.'streams'.'mp4'.'size') -lt 100000000) {
                    you-get.exe -o Downloaded --format=mp4 $line
                    break
                }
                else {
                    break
                }
            }
            Catch{
                continue
            }
        }
    }
}

get-content -encoding UTF8 vlist.txt | Select-Object -skip 2 | set-content -encoding UTF8 "tmp.txt"

Move-Item tmp.txt vlist.txt -Force