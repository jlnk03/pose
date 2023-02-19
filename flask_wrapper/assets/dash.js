bod = document.body
// bod.className = "bg-gradient-to-br from-amber-50 to-violet-50"
// bod.style.backgroundColor = "rgba(250, 247, 245, 1)"
bod.className = "dark:bg-slate-900 bg-[#FAF7F5]"

switchColorMode = () => {
    let interval = setInterval(function () {
    if (darkMode) {
                let element = document.getElementsByClassName("xtick");
                if (element.length > 0) {
                    clearInterval(interval);
                    // console.log("dark mode detected")

                    let plots = document.getElementsByClassName("js-plotly-plot")
                    for (let i = 0; i < plots.length; i++) {
                        // console.log(plots[i])
                        // console.log(plots[i].layout.yaxis.ticksuffix)
                        try {
                            Plotly.update(
                            plots[i], {}, {
                                titlefont: {
                                    color: "white"
                                },
                                xaxis: {
                                    tickfont: {
                                        color: "white"
                                    },
                                    titlefont: {
                                        color: "white"
                                    },
                                    ticksuffix: "s"
                                },
                                yaxis: {
                                    tickfont: {
                                        color: "white"
                                    },
                                    titlefont: {
                                        color: "white"
                                    },
                                    ticksuffix: plots[i].layout.yaxis.ticksuffix
                                    // title: {
                                    //     text: plots[i].layout.yaxis.title.text
                                    // }
                                },
                                legend: {
                                    font: {
                                        color: "white"
                                    },
                                    orientation: "h"
                                }
                            }
                        )
                            // console.log("updated")
                        }
                        catch (err) {
                            console.log(err)
                        }
                    }
                }
        }

        else {
                let element = document.getElementsByClassName("xtick");
                if (element.length > 0) {
                    clearInterval(interval);
                    // console.log("light mode detected")

                    let plots = document.getElementsByClassName("js-plotly-plot")
                    for (let i = 0; i < plots.length; i++) {
                        // console.log(plots[i])
                        try {
                            Plotly.update(
                            plots[i], {}, {
                                titlefont: {
                                    color: "black"
                                },
                                xaxis: {
                                    tickfont: {
                                        color: "black"
                                    },
                                    titlefont: {
                                        color: "black"
                                    },
                                    // title: {
                                    //     text: plots[i].layout.xaxis.title.text
                                    // },
                                    ticksuffix: "s"
                                },
                                yaxis: {
                                    tickfont: {
                                        color: "black"
                                        },
                                        titlefont: {
                                            color: "black"
                                        },
                                        // title: {
                                        //     text: plots[i].layout.yaxis.title.text
                                        // },
                                        ticksuffix: plots[i].layout.yaxis.ticksuffix
                                },
                                legend: {
                                    font: {
                                        color: "black"
                                    },
                                    orientation: "h"
                                }
                            }
                        )
                            // console.log("updated")
                        }
                        catch (err) {
                            console.log(err)
                        }
                    }
                }
        }
    }, 100);
}


let darkMode = window.matchMedia('(prefers-color-scheme: dark)').matches

switchColorMode()

window
    .matchMedia('(prefers-color-scheme: dark)')
    .addEventListener('change', e => {
        darkMode = e.matches;
        // console.log(darkMode)
        switchColorMode()
    })

document.addEventListener("DOMContentLoaded", function() {
    let interval = setInterval(function () {
        let ancestor = document.getElementById("parent_sequence")
        let main = document.getElementById("main_wrapper")
        let loader = document.getElementById("loader")

        if (ancestor) {
            // console.log("ancestor detected")

            const observerOptions = {
                attributes: true,
                subtree: true
            }

            const ancestorObserver = new MutationObserver(function (mutations) {
                mutations.forEach(function(mutation) {
                    if (mutation.target === document.getElementById("sequence")) {
                        if (mutation.target.getAttribute('data-dash-is-loading') === 'true') {
                            // console.log("loading")
                            main.style.visibility = 'hidden';
                            loader.classList.remove('hidden');
                        } else {
                            // console.log("not loading")
                            main.style.visibility = 'visible';
                            loader.classList.add('hidden');
                        }
                    }
                });
            });

            ancestorObserver.observe(ancestor, observerOptions);

            clearInterval(interval);
        }
    }, 100);
})
