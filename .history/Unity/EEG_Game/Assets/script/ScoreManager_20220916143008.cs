using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;
using TMPro;
using static Position;

public class ScoreManager : MonoBehaviour
{
    // Start is called before the first frame update
    public TextMeshProUGUI leftScore_text;
    public TextMeshProUGUI rightScore_text;

    private int leftScore = 0;
    private int rightScore = 0;
    void Start()
    {
        leftScore_text.text = "Hello World";
    }

    // Update is called once per frame
    void Update()
    {
        
    }
}
