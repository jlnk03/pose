bod = document.body
// bod.className = "bg-gradient-to-br from-amber-50 to-violet-50"
// bod.style.backgroundColor = "rgba(250, 247, 245, 1)"
bod.className = "dark:bg-slate-600 bg-[#FAF7F5]"

// document.addEventListener('DOMContentLoaded', function() {
//     setTimeout(function() {
//         let ticks = document.getElementsByClassName("xtick")
//         let ticksy = document.getElementsByClassName("ytick")
//         let legend = document.getElementsByClassName("legendtext")
//         let title = document.getElementsByClassName("gtitle")
//         let xlabel = document.getElementsByClassName("xtitle")
//         let ylabel = document.getElementsByClassName("ytitle")
//
//         // console.log(ticks)
//         for (let i = 0; i < ticks.length; i++) {
//             ticks[i].children[0].style.fill = ""
//             ticks[i].children[0].classList.add("dark:fill-gray-100")
//             ticks[i].children[0].classList.add("fill-slate-900")
//             // console.log(ticks[i].children[0])
//         }
//         for (let i = 0; i < ticksy.length; i++) {
//             ticksy[i].children[0].style.fill = ""
//             ticksy[i].children[0].classList.add("dark:fill-gray-100")
//             ticksy[i].children[0].classList.add("fill-slate-900")
//         }
//         for (let i = 0; i < legend.length; i++) {
//             legend[i].style.fill = ""
//             legend[i].classList.add("dark:fill-gray-100")
//             legend[i].classList.add("fill-slate-900")
//         }
//         for (let i = 0; i < title.length; i++) {
//             title[i].style.fill = ""
//             title[i].classList.add("dark:fill-gray-100")
//             title[i].classList.add("fill-slate-900")
//         }
//         for (let i = 0; i < xlabel.length; i++) {
//             xlabel[i].style.fill = ""
//             xlabel[i].classList.add("dark:fill-gray-100")
//             xlabel[i].classList.add("fill-slate-900")
//         }
//         for (let i = 0; i < ylabel.length; i++) {
//             ylabel[i].style.fill = ""
//             ylabel[i].classList.add("dark:fill-gray-100")
//             ylabel[i].classList.add("fill-slate-900")
//         }
//
//     }, 500)
// })

// var interval = setInterval(function() {
//   var element = document.getElementsByClassName("xtick");
//   if (element.length > 0) {
//             clearInterval(interval);
//             let ticks = document.getElementsByClassName("xtick")
//             let ticksy = document.getElementsByClassName("ytick")
//             let legend = document.getElementsByClassName("legendtext")
//             let title = document.getElementsByClassName("gtitle")
//             let xlabel = document.getElementsByClassName("xtitle")
//             let ylabel = document.getElementsByClassName("ytitle")
//
//             // console.log(ticks)
//             for (let i = 0; i < ticks.length; i++) {
//                 ticks[i].children[0].style.fill = ""
//                 ticks[i].children[0].classList.add("dark:fill-gray-100")
//                 ticks[i].children[0].classList.add("fill-slate-900")
//                 // console.log(ticks[i].children[0])
//             }
//             for (let i = 0; i < ticksy.length; i++) {
//                 ticksy[i].children[0].style.fill = ""
//                 ticksy[i].children[0].classList.add("dark:fill-gray-100")
//                 ticksy[i].children[0].classList.add("fill-slate-900")
//             }
//             for (let i = 0; i < legend.length; i++) {
//                 legend[i].style.fill = ""
//                 legend[i].classList.add("dark:fill-gray-100")
//                 legend[i].classList.add("fill-slate-900")
//             }
//             for (let i = 0; i < title.length; i++) {
//                 title[i].style.fill = ""
//                 title[i].classList.add("dark:fill-gray-100")
//                 title[i].classList.add("fill-slate-900")
//             }
//             for (let i = 0; i < xlabel.length; i++) {
//                 xlabel[i].style.fill = ""
//                 xlabel[i].classList.add("dark:fill-gray-100")
//                 xlabel[i].classList.add("fill-slate-900")
//             }
//             for (let i = 0; i < ylabel.length; i++) {
//                 ylabel[i].style.fill = ""
//                 ylabel[i].classList.add("dark:fill-gray-100")
//                 ylabel[i].classList.add("fill-slate-900")
//             }
//         }
// }, 100);

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

document.addEventListener('DOMContentLoaded', function() {
    let interval = setInterval(function () {
    let navbar = document.getElementById("file_list")
    // console.log(navbar)
    if (navbar) {
        clearInterval(interval);

        const observer = new MutationObserver(function (mutations) {
            // console.log("mutation detected")
            mutations.forEach(function (mutation) {
                // console.log(mutation.type);
                switchColorMode()
            });
        });

        const observerOptions = {
            attributes: true,
            childList: true,
            characterData: true
        };

        observer.observe(navbar, observerOptions);
    }
    }, 100);
});


// if (darkMode) {
//     let interval = setInterval(function () {
//         let element = document.getElementsByClassName("xtick");
//         if (element.length > 0) {
//             clearInterval(interval);
//             // console.log("dark mode detected")
//
//             let plots = document.getElementsByClassName("js-plotly-plot")
//             for (let i = 0; i < plots.length; i++) {
//                 // console.log(plots[i])
//                 try {
//                     Plotly.update(
//                     plots[i], {}, {
//                         titlefont: {
//                             color: "white"
//                         },
//                         xaxis: {
//                             tickfont: {
//                                 color: "white"
//                             },
//                             titlefont: {
//                                 color: "white"
//                             },
//                             title: {
//                                 text: plots[i].layout.xaxis.title.text
//                             },
//                             ticksuffix: "s"
//                         },
//                         yaxis: {
//                             tickfont: {
//                                 color: "white"
//                             },
//                             titlefont: {
//                                 color: "white"
//                             },
//                             title: {
//                                 text: plots[i].layout.yaxis.title.text
//                             }
//                         },
//                         legend: {
//                             font: {
//                                 color: "white"
//                             },
//                             orientation: "h"
//                         }
//                     }
//                 )
//                     // console.log("updated")
//                 }
//                 catch (err) {
//                     console.log(err)
//                 }
//             }
//         }
//     }, 100);
// }