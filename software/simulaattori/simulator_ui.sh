#!/usr/bin/env bash

BASE_URL="http://localhost:8000"
clear
# -------------------------
# Helper: GET current values
# -------------------------

get_depth() {
    
    echo ""
    echo "Kameran syvyys arvot"
    echo "=========================================================="
    curl -s "$BASE_URL/depth"
    echo ""
    echo "=========================================================="
    echo ""
    
}

get_imu() {
    
    echo ""
    echo " Imun arvot"
    echo "==========================================================="
    curl -s "$BASE_URL/IMU"
    echo ""
    echo "==========================================================="
    echo ""
    
    
}

get_io() {
    
    echo ""
    echo "IO tilat"
    echo "=========================================================="
    curl -s "$BASE_URL/IO"
    echo ""
    echo "=========================================================="
    echo ""
    

}

# --------------------------------
# Parsers (olettaa JSON-vastauksen)
# esim: {"left":10,"center":20,"right":30}
# --------------------------------

parse_json_value() {
    local json="$1"
    local key="$2"
   echo "$json" | grep -o "\"$key\":[^,}]*" | head -n1 | cut -d':' -f2 | tr -d ' "'

}
# -------------------------
# Setters
# -------------------------
get_depth_json() {
    curl -s "$BASE_URL/depth"
}
set_depth() {
    clear
    local json
    json=$(get_depth_json)

    local left center right
    left=$(parse_json_value "$json" left)
    center=$(parse_json_value "$json" center)
    right=$(parse_json_value "$json" right)

    # --- varmista että arvot ovat olemassa ---
    for v in left center right; do
    if [[ -z "${!v}" || "${!v}" == "null" ]]; then
        echo "Virhe: $v puuttuu (JSON parse epäonnistui)"
        return 1
    fi
done

    # --- käyttäjän syötteet ---
    for arg in "$@"; do
        case "$arg" in
            left=*|center=*|right=*)
                local key="${arg%%=*}"
                local value="${arg#*=}"
                printf -v "$key" "%s" "$value"
                ;;
            *)
                echo "Virheellinen parametri: $arg"
                return 1
                ;;
        esac
    done

    # --- validointi: hyväksytään numerot + inf, -inf, nan, none ---
    for v in left center right; do
    if ! [[ "${!v}" =~ ^(-?[0-9]+(\.[0-9]+)?|inf|-inf|nan|none)$ ]]; then
        echo "Virhe: $v sisältää epävalidin arvon (${!v})"
        return 1
    fi
done

    echo ""
    echo "Kameran syvyys arvot muutettu"
    echo "=========================================================="
    curl -s -X POST "$BASE_URL/set_depth?left=$left&center=$center&right=$right"
    echo ""
    echo "=========================================================="
    echo ""
}

set_imu() {
    if [ "$#" -lt 1 ]; then
        echo "Käyttö: set_imu roll_deg=... pitch_deg=... yaw_deg=..."
        return 1
    fi

    local json
    json=$(get_imu)

    # UI-nimet
    local roll_deg pitch_deg yaw_deg
    roll_deg=$(parse_json_value "$json" roll_deg)
    pitch_deg=$(parse_json_value "$json" pitch_deg)
    yaw_deg=$(parse_json_value "$json" yaw_deg)

    for arg in "$@"; do
        case "$arg" in
            roll_deg=*)
                roll_deg="${arg#*=}"
                ;;
            pitch_deg=*)
                pitch_deg="${arg#*=}"
                ;;
            yaw_deg=*)
                yaw_deg="${arg#*=}"
                ;;
            *)
                echo "Virheellinen parametri: $arg"
                return 1
                ;;
        esac
    done

    echo "IMU tila muutettu"
    echo "======================================"

    curl -s -X POST \
        "$BASE_URL/set_IMU?x=$roll_deg&y=$pitch_deg&z=$yaw_deg"

    echo
    echo "======================================"
}



set_io() {
    clear
    if [ "$#" -lt 1 ]; then
        echo "Käyttö: IO1=0 IO3=1 IO5=0"
        return 1
    fi

    local json
    json=$(get_io)

    local IO1 IO2 IO3 IO4 IO5
    IO1=$(parse_json_value "$json" IO1)
    IO2=$(parse_json_value "$json" IO2)
    IO3=$(parse_json_value "$json" IO3)
    IO4=$(parse_json_value "$json" IO4)
    IO5=$(parse_json_value "$json" IO5)

    for arg in "$@"; do
        case "$arg" in
            IO[1-5]=*)
                local key="${arg%%=*}"
                local value="${arg#*=}"
                printf -v "$key" "%s" "$value"
                ;;
            *)
                echo "Virheellinen parametri: $arg (käytä IO1=..IO5=..)"
                return 1
                ;;
        esac
    done
    echo ""
    echo IO tila muutettu
    echo "==============================================================="
    curl -s -X POST \
        "$BASE_URL/set_IO?IO1=$IO1&IO2=$IO2&IO3=$IO3&IO4=$IO4&IO5=$IO5"
    echo ""
    echo "==============================================================="
    echo ""
    
}

# -------------------------
# UI Menu
# -------------------------
get_depth && get_imu && get_io

while true; do
    echo
    echo "=== Sensor UI ==="
    echo "1) Näytä kaikki"
    echo "2) Näytä depth"
    echo "3) Näytä IMU"
    echo "4) Näytä IO"
    echo "5) Aseta depth"
    echo "6) Aseta IMU"
    echo "7) Aseta IO"
    echo "q) Poistu"
    read -rp "> " choice

    case "$choice" in
        1) clear && get_depth && get_imu && get_io ;;
        2) clear && get_depth ;;
        3) clear && get_imu ;;
        4) clear && get_io ;;
        5)  
            clear
            echo
            echo "Arvot tällä hetkellä"
            get_depth
            read -rp "Anna syvyys (esim. left=300 center=500 right=800 tai vain center=800): " line
            set_depth $line
            ;;
        6)  
            clear
            echo
            echo "Arvot tällä hetkellä"
            get_imu
            read -rp "Anna imu arvo (esim. roll_deg=1 yaw_deg=3) " line
            set_imu $line
            ;;
        7)  
            clear
            echo
            echo "Arvot tällä hetkellä"
            get_io
            read -rp "Anna IO-muutokset (esim: IO1=1 IO3=0): " line
            set_io $line
            ;;
        q) return 0 ;;
        *) echo "Tuntematon valinta" ;;
    esac
done


