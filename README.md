# WELT: Web Energy Labeling Tool

## Getting Started
When using a laptop, make sure it's plugged.
### Tools
#### [Scaphandre](https://github.com/hubblo-org/scaphandre)
Scaphandre supports Windows 10 and 11, and Linux, **not macOS**.
#### [CodeCarbon](https://mlco2.github.io/codecarbon/)
CodeCarbon works with Apple M1 and M2 processors or [one of these](https://web.eece.maine.edu/~vweaver/projects/rapl/).

### Configuration
This test can be configured using `config.toml`.

| Key             | Description                                      | Values                 |
|-----------------|--------------------------------------------------|------------------------|
| tool            | Measurement tool                                 | codecarbon, scaphandre |
| scaphandre_path | Path to scaphandre binary                        | str                    |
| browser         | Browser used for testing                         | firefox, chrome        |
| dataset         | List of URLs to use in JSON format               | str                    |
| duration        | Measurement duration                             | int                    |
| delay           | Delay between measurements                       | int                    |
| repeat          | How many times the experiment should be repeated | int                    |

## Websites
The website list is a combination of the most popular websites as analyzed by SimilarWeb and Semrush.

## Measurement
Measurements are done in three steps.
1. Operating System (Idle)
2. Empty browser tab
3. Website

## Troubleshooting
### No access to Intel RAPL on Linux
Intel RAPL requires root access.
```commandline
# chmod -R a+r /sys/class/powercap/intel-rapl
```
### Another instance of codecarbon is already running
```commandline
$ rm /tmp/.codecarbon.lock
```
