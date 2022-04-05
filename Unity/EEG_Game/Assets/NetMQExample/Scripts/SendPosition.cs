using System;
using System.Collections;
using System.Threading;
using System.Collections.Generic;
using UnityEngine;
using AsyncIO;
using NetMQ;
using NetMQ.Sockets;


public class SendPosition : MonoBehaviour
{   
    Thread mThread;
    bool running;
    GameObject cube;

    Vector3 pos = new Vector3(-1.54f,-0.49f,0);
    Vector3 startPos = new Vector3(-1.54f,-0.49f,0);
    // Start is called before the first frame update
    void Start()
    {
        cube = GameObject.FindWithTag("Player");
        cube.transform.position = startPos;
        ThreadStart ts = new ThreadStart(Run);
        mThread = new Thread(ts);
        mThread.Start();
        running = true;
    }

    // Update is called once per frame
    void Update()
    {
        cube.transform.position = pos;
    }
    void Run()
    {
        ForceDotNet.Force(); // this line is needed to prevent unity freeze after one use, not sure why yet
        using (RequestSocket client = new RequestSocket())
        {
            client.Connect("tcp://localhost:5555");

            for (int i = 0; i < 10 && running; i++)
            {
                Debug.Log("Sending Result");
                client.SendFrame("Hello");
                // ReceiveFrameString() blocks the thread until you receive the string, but TryReceiveFrameString()
                // do not block the thread, you can try commenting one and see what the other does, try to reason why
                // unity freezes when you use ReceiveFrameString() and play and stop the scene without running the server
//                string message = client.ReceiveFrameString();
//                Debug.Log("Received: " + message);
                string message = null;
                bool gotMessage = false;
                byte[] messageByte = null;
                while (running)
                {
                    gotMessage = client.TryReceiveFrameBytes(out messageByte); // this returns true if it's successful
                    if (gotMessage) break;
                }

                if (gotMessage)
                {
                    message = System.Text.Encoding.UTF8.GetString(messageByte);
                    Debug.Log("Raw messsage"+message);
                    Debug.Log("Type " + message.GetType().FullName);
                    pos = moveBall(message);
                }
            }
        }

        NetMQConfig.Cleanup(); // this line is needed to prevent unity freeze after one use, not sure why yet
    }

    public static Vector3 moveBall(string message)
    {   
        string dec = "";
        long decision = 0;
        Vector3 moveVec = new Vector3(0,0,0);
        if (message.StartsWith("(") && message.EndsWith(")"))
        {
            dec = message.Substring(1, message.Length - 2);
            decision = Int64.Parse(dec);
            //Debug.Log("vector"+sVector);
        }
        else{
            decision = Int64.Parse(message);
        }
        if (decision == 1)
        {
            moveVec = new Vector3(5,-0.49f,0);
        }
        else if (decision == 2)
        {
            moveVec = new Vector3(-5,-0.49f,0);
        }
        else{
            moveVec = new Vector3(-1.54f,-0.49f,0);
        }
        return moveVec;
    }




}
