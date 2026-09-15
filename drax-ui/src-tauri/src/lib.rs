use std::{
    io::{BufRead, BufReader, Write},
    process::{Child, Command, Stdio},
    sync::Mutex,
};

use tauri::{Emitter, Manager, State};


// ============================================================
// DRAX PYTHON PROCESS
// ============================================================

struct DraxProcess {

    // Keep Python alive for the lifetime of the app.
    _child: Mutex<Option<Child>>,

    // Tauri -> Python communication.
    stdin: Mutex<Option<std::process::ChildStdin>>,
}


// ============================================================
// SEND MESSAGE TO PYTHON
// ============================================================

#[tauri::command]
async fn send_to_drax(
    message: String,
    state: State<'_, DraxProcess>,
) -> Result<(), String> {

    let mut stdin_guard = state
        .stdin
        .lock()
        .map_err(|_| {
            "Failed to lock Drax bridge.".to_string()
        })?;

    let stdin = stdin_guard
        .as_mut()
        .ok_or_else(|| {
            "Drax bridge is not running.".to_string()
        })?;

    let payload = serde_json::json!({
        "type": "chat",
        "text": message
    });


    // Send one JSON object per line.
    writeln!(
        stdin,
        "{}",
        payload
    )
    .map_err(|error| {
        format!(
            "Failed to send command to Drax: {error}"
        )
    })?;


    // Immediately push the command to Python.
    stdin
        .flush()
        .map_err(|error| {
            format!(
                "Failed to flush Drax command: {error}"
            )
        })?;


    Ok(())
}


// ============================================================
// TAURI ENTRY POINT
// ============================================================

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {

    tauri::Builder::default()

        .setup(|app| {

            // =================================================
            // FIND PROJECT ROOT
            // =================================================

            let project_root =
                std::path::PathBuf::from(
                    env!("CARGO_MANIFEST_DIR")
                )
                .parent()
                .unwrap()
                .parent()
                .unwrap()
                .to_path_buf();


            let bridge_path =
                project_root.join("bridge.py");


            println!(
                "Starting Drax bridge:"
            );

            println!(
                "{}",
                bridge_path.display()
            );


            // =================================================
            // START PYTHON BRIDGE
            // =================================================

            let mut child =
                Command::new("python")

                    // -----------------------------------------
                    // IMPORTANT
                    //
                    // -u = unbuffered Python stdout/stderr.
                    //
                    // This is critical because the Python
                    // bridge stays alive instead of exiting
                    // after every command.
                    // -----------------------------------------

                    .arg("-u")

                    .arg(&bridge_path)

                    // -----------------------------------------
                    // Standard streams
                    // -----------------------------------------

                    .stdin(
                        Stdio::piped()
                    )

                    .stdout(
                        Stdio::piped()
                    )

                    .stderr(
                        Stdio::inherit()
                    )

                    // -----------------------------------------
                    // Run from DraxAgent root
                    // -----------------------------------------

                    .current_dir(
                        &project_root
                    )

                    // -----------------------------------------
                    // Tell terminal.py that we're running
                    // through the GUI bridge.
                    // -----------------------------------------

                    .env(
                        "DRAX_BRIDGE",
                        "1"
                    )

                    // -----------------------------------------
                    // Force UTF-8.
                    // -----------------------------------------

                    .env(
                        "PYTHONUTF8",
                        "1"
                    )

                    .env(
                        "PYTHONIOENCODING",
                        "utf-8"
                    )

                    // -----------------------------------------
                    // Explicitly disable Python buffering too.
                    // This gives us a second layer of protection
                    // in case Python/environment behavior changes.
                    // -----------------------------------------

                    .env(
                        "PYTHONUNBUFFERED",
                        "1"
                    )

                    .spawn()

                    .map_err(|error| {

                        format!(
                            "Failed to start Python bridge: {error}"
                        )

                    })?;


            // =================================================
            // TAKE PYTHON STDIN
            // =================================================

            let stdin =
                child.stdin.take();


            // =================================================
            // TAKE PYTHON STDOUT
            // =================================================

            let stdout =
                child.stdout.take();


            // =================================================
            // PYTHON -> TAURI EVENT READER
            // =================================================

            if let Some(stdout) = stdout {

                let app_handle =
                    app.handle().clone();


                std::thread::spawn(
                    move || {

                        let reader =
                            BufReader::new(
                                stdout
                            );


                        // -------------------------------------
                        // Read one JSONL message at a time.
                        // -------------------------------------

                        for line_result in reader.lines() {

                            match line_result {

                                Ok(line) => {

                                    let line =
                                        line.trim();


                                    if line.is_empty() {
                                        continue;
                                    }


                                    // ---------------------------------
                                    // Python bridge uses JSONL.
                                    // ---------------------------------

                                    match serde_json::from_str::<
                                        serde_json::Value
                                    >(line) {

                                        Ok(message) => {

                                            // Send Python event
                                            // into the Tauri frontend.
                                            let _ =
                                                app_handle.emit(
                                                    "drax://message",
                                                    message
                                                );
                                        }


                                        Err(error) => {

                                            // Some existing Drax
                                            // backend debug lines
                                            // such as [Memory] and
                                            // [Decision] are not JSON.
                                            //
                                            // Ignore them instead of
                                            // treating them as fatal.

                                            eprintln!(
                                                "Ignoring non-JSON Drax output: {error}"
                                            );

                                            eprintln!(
                                                "Bridge output: {line}"
                                            );
                                        }
                                    }
                                }


                                Err(error) => {

                                    eprintln!(
                                        "Drax bridge stdout error: {error}"
                                    );

                                    break;
                                }
                            }
                        }


                        eprintln!(
                            "Drax Python bridge stdout closed."
                        );
                    }
                );
            }


            // =================================================
            // STORE PROCESS STATE
            // =================================================

            app.manage(
                DraxProcess {

                    _child:
                        Mutex::new(
                            Some(child)
                        ),

                    stdin:
                        Mutex::new(
                            stdin
                        ),
                }
            );


            Ok(())
        })


        // ====================================================
        // TAURI COMMANDS
        // ====================================================

        .invoke_handler(
            tauri::generate_handler![
                send_to_drax
            ]
        )


        // ====================================================
        // RUN APPLICATION
        // ====================================================

        .run(
            tauri::generate_context!()
        )

        .expect(
            "error while running Drax"
        );
}